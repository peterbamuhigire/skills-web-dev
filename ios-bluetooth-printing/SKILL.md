---
name: ios-bluetooth-printing
description: CoreBluetooth integration for ESC/POS thermal printer communication on iOS. Covers BLE discovery, pairing, characteristic writing, ESC/POS command translation from Android, and receipt formatting. Use when connecting iOS apps to Bluetooth thermal...
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities.

# iOS Bluetooth Thermal Printing (ESC/POS over BLE)

CoreBluetooth-based integration for ESC/POS thermal printers on iOS. Direct translation of Android `BluetoothPrinter.kt` and `EscPosReceipt.kt` patterns into Swift/SwiftUI.

**Stack:** Swift 5.9+ | CoreBluetooth | SwiftUI | ESC/POS byte protocol
**Min iOS:** 16.0 | **Target iOS:** 18.x
**Android Parity:** Receipt output must be byte-identical to `EscPosReceipt.kt`

## When to Use

- Connecting an iOS app to a Bluetooth thermal printer
- Printing receipts, invoices, or labels from an iOS POS or SaaS app
- Porting Android ESC/POS printing to iOS

## When NOT to Use

- AirPrint / network printers (use UIPrintInteractionController)
- USB/serial printers (not BLE)
- PDF generation without physical printing

---

## 1. CoreBluetooth Architecture

```swift
import CoreBluetooth

enum ConnectionState: String {
    case disconnected, scanning, connecting, discoveringServices, ready, error
}

class BluetoothPrinterManager: NSObject, ObservableObject {
    @Published var discoveredPrinters: [CBPeripheral] = []
    @Published var connectedPrinter: CBPeripheral?
    @Published var isScanning = false
    @Published var connectionState: ConnectionState = .disconnected
    @Published var lastError: String?

    private var centralManager: CBCentralManager!
    private var writeCharacteristic: CBCharacteristic?
    private var printCompletion: ((Result<Void, Error>) -> Void)?

    // Standard ESC/POS BLE UUIDs — works with Epson, Star, generic printers
    private let printerServiceUUID = CBUUID(string: "49535343-FE7D-4AE5-8FA9-9FAFD205E455")
    private let writeCharUUID = CBUUID(string: "49535343-8841-43F4-A8D4-ECBE34729BB3")

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: .main)
    }

    func startScanning() {
        guard centralManager.state == .poweredOn else { lastError = "Bluetooth not powered on"; return }
        discoveredPrinters.removeAll()
        isScanning = true
        connectionState = .scanning
        centralManager.scanForPeripherals(
            withServices: [printerServiceUUID],
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
        )
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) { [weak self] in self?.stopScanning() }
    }

    func stopScanning() {
        centralManager.stopScan()
        isScanning = false
        if connectionState == .scanning { connectionState = .disconnected }
    }

    func connect(to peripheral: CBPeripheral) {
        stopScanning()
        connectionState = .connecting
        peripheral.delegate = self
        centralManager.connect(peripheral, options: nil)
    }

    func disconnect() {
        if let printer = connectedPrinter { centralManager.cancelPeripheralConnection(printer) }
        connectedPrinter = nil; writeCharacteristic = nil; connectionState = .disconnected
    }
}
```

---

## 2. CBCentralManagerDelegate

```swift
extension BluetoothPrinterManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn: lastError = nil
        case .poweredOff: lastError = "Bluetooth is turned off"; connectionState = .disconnected
        case .unauthorized: lastError = "Bluetooth permission denied"; connectionState = .error
        case .unsupported: lastError = "Bluetooth not supported"; connectionState = .error
        default: lastError = "Bluetooth unavailable"
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral,
                         advertisementData: [String: Any], rssi RSSI: NSNumber) {
        if !discoveredPrinters.contains(where: { $0.identifier == peripheral.identifier }) {
            discoveredPrinters.append(peripheral)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        connectedPrinter = peripheral
        connectionState = .discoveringServices
        peripheral.discoverServices([printerServiceUUID])
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        connectionState = .error; lastError = error?.localizedDescription ?? "Connection failed"
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        if peripheral.identifier == connectedPrinter?.identifier {
            connectedPrinter = nil; writeCharacteristic = nil; connectionState = .disconnected
            if let error { lastError = "Disconnected: \(error.localizedDescription)" }
        }
    }
}
```

---

## 3. CBPeripheralDelegate

```swift
extension BluetoothPrinterManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard error == nil,
              let service = peripheral.services?.first(where: { $0.uuid == printerServiceUUID })
        else { connectionState = .error; lastError = "Printer service not found"; return }
        peripheral.discoverCharacteristics([writeCharUUID], for: service)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard error == nil,
              let characteristic = service.characteristics?.first(where: { $0.uuid == writeCharUUID })
        else { connectionState = .error; lastError = "Write characteristic not found"; return }
        writeCharacteristic = characteristic
        connectionState = .ready
    }

    func peripheral(_ peripheral: CBPeripheral, didWriteValueFor characteristic: CBCharacteristic, error: Error?) {
        if let error { printCompletion?(.failure(error)); printCompletion = nil }
    }
}
```

---

## 4. ESC/POS Commands (Direct Translation from Android)

Byte-for-byte identical to Android `EscPosReceipt.kt`. All hex values match.

```swift
enum EscPos {
    static let INIT: [UInt8] = [0x1B, 0x40]
    static let BOLD_ON: [UInt8] = [0x1B, 0x45, 0x01]
    static let BOLD_OFF: [UInt8] = [0x1B, 0x45, 0x00]
    static let UNDERLINE_ON: [UInt8] = [0x1B, 0x2D, 0x01]
    static let UNDERLINE_OFF: [UInt8] = [0x1B, 0x2D, 0x00]
    static let ALIGN_LEFT: [UInt8] = [0x1B, 0x61, 0x00]
    static let ALIGN_CENTER: [UInt8] = [0x1B, 0x61, 0x01]
    static let ALIGN_RIGHT: [UInt8] = [0x1B, 0x61, 0x02]
    static let DOUBLE_HEIGHT: [UInt8] = [0x1B, 0x21, 0x10]
    static let DOUBLE_WIDTH: [UInt8] = [0x1B, 0x21, 0x20]
    static let DOUBLE_SIZE: [UInt8] = [0x1B, 0x21, 0x30]
    static let NORMAL_SIZE: [UInt8] = [0x1B, 0x21, 0x00]
    static let CUT_PAPER: [UInt8] = [0x1D, 0x56, 0x00]
    static let PARTIAL_CUT: [UInt8] = [0x1D, 0x56, 0x01]
    static let FEED_LINES: [UInt8] = [0x1B, 0x64, 0x05]

    static func text(_ string: String) -> [UInt8] {
        if let data = string.data(using: .windowsCP1252) { return Array(data) }
        return Array(string.utf8)  // Fallback
    }

    static func feedLines(_ count: UInt8) -> [UInt8] { [0x1B, 0x64, count] }
}
```

---

## 5. Receipt Builder (Mirrors Android EscPosReceipt)

Fluent builder producing the same byte output as Android `EscPosReceipt.kt`.

```swift
class EscPosReceipt {
    private var buffer: [UInt8] = []
    private let paperWidth: Int  // 32 for 58mm, 48 for 80mm

    init(paperWidth: Int = 32) { self.paperWidth = paperWidth }

    @discardableResult func initialize() -> Self { buffer.append(contentsOf: EscPos.INIT); return self }
    @discardableResult func text(_ s: String) -> Self { buffer.append(contentsOf: EscPos.text(s)); return self }
    @discardableResult func line(_ s: String) -> Self { buffer.append(contentsOf: EscPos.text(s + "\n")); return self }

    @discardableResult func bold(_ s: String) -> Self {
        buffer += EscPos.BOLD_ON + EscPos.text(s) + EscPos.BOLD_OFF; return self
    }

    @discardableResult func centered(_ s: String) -> Self {
        buffer += EscPos.ALIGN_CENTER + EscPos.text(s + "\n") + EscPos.ALIGN_LEFT; return self
    }

    @discardableResult func centeredBold(_ s: String) -> Self {
        buffer += EscPos.ALIGN_CENTER + EscPos.BOLD_ON + EscPos.text(s + "\n") + EscPos.BOLD_OFF + EscPos.ALIGN_LEFT
        return self
    }

    @discardableResult func doubleSize(_ s: String) -> Self {
        buffer += EscPos.DOUBLE_SIZE + EscPos.text(s + "\n") + EscPos.NORMAL_SIZE; return self
    }

    /// Two-column row — mirrors Android EscPosReceipt.leftRight()
    @discardableResult func leftRight(_ left: String, _ right: String) -> Self {
        let maxLeft = paperWidth - right.count - 1
        let trimmed = String(left.prefix(maxLeft))
        let spaces = String(repeating: " ", count: max(paperWidth - trimmed.count - right.count, 1))
        buffer += EscPos.text(trimmed + spaces + right + "\n"); return self
    }

    /// Three-column item line: qty, description, amount
    @discardableResult func itemLine(qty: String, desc: String, amount: String) -> Self {
        let qtyW = 4; let amtW = amount.count + 1; let descW = paperWidth - qtyW - amtW
        let d = String(desc.prefix(descW))
        let row = qty.padding(toLength: qtyW, withPad: " ", startingAt: 0)
            + d + String(repeating: " ", count: descW - d.count) + amount + "\n"
        buffer += EscPos.text(row); return self
    }

    @discardableResult func separator(char: Character = "-") -> Self {
        buffer += EscPos.text(String(repeating: char, count: paperWidth) + "\n"); return self
    }

    @discardableResult func blankLine() -> Self { buffer += EscPos.text("\n"); return self }
    @discardableResult func feed(lines: Int = 3) -> Self { buffer += EscPos.feedLines(UInt8(min(lines, 255))); return self }
    @discardableResult func cut() -> Self { buffer += EscPos.CUT_PAPER; return self }
    func build() -> Data { Data(buffer) }
}
```

---

## 6. Printing Data (Chunked BLE Writes)

```swift
extension BluetoothPrinterManager {
    func printReceipt(_ data: Data, completion: ((Result<Void, Error>) -> Void)? = nil) {
        guard let peripheral = connectedPrinter, let characteristic = writeCharacteristic
        else { completion?(.failure(PrinterError.notConnected)); return }
        guard connectionState == .ready else { completion?(.failure(PrinterError.notReady)); return }

        let chunkSize = min(peripheral.maximumWriteValueLength(for: .withResponse), 182)
        printCompletion = completion

        for (i, chunk) in data.chunked(into: chunkSize).enumerated() {
            peripheral.writeValue(chunk, for: characteristic, type: .withResponse)
            if i < data.count / chunkSize { Thread.sleep(forTimeInterval: 0.05) }
        }
    }
}

enum PrinterError: LocalizedError {
    case notConnected, notReady, writeFailed(String)
    var errorDescription: String? {
        switch self {
        case .notConnected: return "No printer connected"
        case .notReady: return "Printer not ready"
        case .writeFailed(let msg): return "Write failed: \(msg)"
        }
    }
}

extension Data {
    func chunked(into size: Int) -> [Data] {
        stride(from: 0, to: count, by: size).map { subdata(in: $0..<Swift.min($0 + size, count)) }
    }
}
```

---

## 7. Info.plist Required Keys

```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>Connect to Bluetooth thermal printers for receipt printing</string>

<!-- OPTIONAL: only if printing must work in background -->
<key>UIBackgroundModes</key>
<array><string>bluetooth-central</string></array>
```

**Xcode:** Target > Info > add `Privacy - Bluetooth Always Usage Description`. For background: Signing & Capabilities > Background Modes > Uses Bluetooth LE accessories.

---

## 8. SwiftUI Integration

```swift
struct PrinterSelectionView: View {
    @StateObject private var printer = BluetoothPrinterManager()

    var body: some View {
        List {
            Section("Available Printers") {
                if printer.isScanning {
                    HStack { ProgressView(); Text("Scanning...") }
                } else if printer.discoveredPrinters.isEmpty {
                    Text("No printers found").foregroundStyle(.secondary)
                }
                ForEach(printer.discoveredPrinters, id: \.identifier) { device in
                    Button { printer.connect(to: device) } label: {
                        HStack {
                            Image(systemName: "printer")
                            Text(device.name ?? "Unknown Printer")
                            Spacer()
                            if printer.connectedPrinter?.identifier == device.identifier {
                                Image(systemName: "checkmark.circle.fill").foregroundStyle(.green)
                            }
                        }
                    }
                }
            }
            if let error = printer.lastError {
                Section("Status") { Text(error).foregroundStyle(.red) }
            }
        }
        .navigationTitle("Select Printer")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(printer.isScanning ? "Stop" : "Scan") {
                    printer.isScanning ? printer.stopScanning() : printer.startScanning()
                }
            }
        }
    }
}

struct PrintReceiptButton: View {
    @EnvironmentObject var printerManager: BluetoothPrinterManager
    let receiptData: Data
    var body: some View {
        Button { printerManager.printReceipt(receiptData) } label: {
            Label("Print Receipt", systemImage: "printer")
        }
        .disabled(printerManager.connectionState != .ready)
    }
}
```

---

## 9. Example: Full Receipt

```swift
func buildSaleReceipt(businessName: String, receiptNo: String,
    items: [(qty: Int, name: String, amount: String)],
    subtotal: String, tax: String, total: String, cashier: String) -> Data {
    let r = EscPosReceipt(paperWidth: 32).initialize()
        .centeredBold(businessName).centered("Receipt #\(receiptNo)").separator()
    for item in items { r.itemLine(qty: "\(item.qty)x", desc: item.name, amount: item.amount) }
    r.separator().leftRight("Subtotal:", subtotal).leftRight("Tax:", tax)
        .separator(char: "=").bold("TOTAL: \(total)\n").blankLine()
        .centered("Served by: \(cashier)").centered("Thank you!").feed(lines: 4).cut()
    return r.build()
}
```

---

## 10. Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `centralManagerDidUpdateState` never fires | CBCentralManager not retained | Store as instance property |
| No printers discovered | No UUID filter or printer off | Filter by `printerServiceUUID`; check power/range |
| Write fails silently | Chunk exceeds BLE MTU | Use `maximumWriteValueLength(for:)`, cap at 182 |
| Garbled text | Wrong encoding | Use `windowsCP1252`, not UTF-8 |
| Disconnects mid-print | Buffer overflow | 50ms delay between chunks; use `.withResponse` |
| App crashes on launch | Missing Info.plist key | Add `NSBluetoothAlwaysUsageDescription` |
| Some printers need `.withoutResponse` | Char properties mismatch | Check `characteristic.properties` and adapt |
| Receipt too wide/narrow | Wrong paper width | 58mm = 32 chars, 80mm = 48 chars |

---

## 11. Reconnection

```swift
extension BluetoothPrinterManager {
    func reconnect(to identifier: UUID) {
        let peripherals = centralManager.retrievePeripherals(withIdentifiers: [identifier])
        if let p = peripherals.first { connect(to: p) }
        else { lastError = "Previously connected printer not found" }
    }

    func saveLastPrinter() {
        guard let id = connectedPrinter?.identifier.uuidString else { return }
        UserDefaults.standard.set(id, forKey: "lastPrinterIdentifier")
    }

    func reconnectLastPrinter() {
        guard let s = UserDefaults.standard.string(forKey: "lastPrinterIdentifier"),
              let uuid = UUID(uuidString: s) else { return }
        reconnect(to: uuid)
    }
}
```

---

## 12. Implementation Checklist

- [ ] `BluetoothPrinterManager` with CBCentralManager + CBPeripheralDelegate
- [ ] `NSBluetoothAlwaysUsageDescription` in Info.plist
- [ ] ESC/POS bytes identical to Android `EscPosReceipt.kt`
- [ ] Chunked writes respecting BLE MTU (capped at 182 bytes)
- [ ] Printer discovery filtered by service UUID
- [ ] Connection state management with `@Published` properties
- [ ] `EscPosReceipt` builder matching Android receipt byte output
- [ ] SwiftUI printer selection view with scan/connect/status
- [ ] Error handling for all BLE failure modes
- [ ] Auto-reconnect to last known printer
- [ ] Character encoding: `windowsCP1252` for receipt symbols
- [ ] Paper width configurable (32 for 58mm, 48 for 80mm)
- [ ] Print button disabled when printer not `.ready`

## Anti-Patterns

- **Never** use `CBCentralManager(delegate: self, queue: nil)` with background writes -- use `.main` or a serial queue
- **Never** send the entire receipt as one write -- always chunk
- **Never** hardcode MTU size -- always query `maximumWriteValueLength(for:)`
- **Never** use `.withoutResponse` as default -- prefer `.withResponse`, fall back only when required
- **Never** skip the `INIT` command (`0x1B 0x40`) -- printers may retain stale formatting
- **Never** use UTF-8 encoding for receipt text -- thermal printers expect `windowsCP1252`
