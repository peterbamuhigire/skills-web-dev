# ios-swift-recipes Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `2. Reusable NumberFormatter (Critical for scroll performance)`
- `3. ISO 8601 Date Handling`
- `4. Encodable/Decodable Universal Extensions`
- `5. Custom Decoder — Handle API Type Mismatches`
- `6. Type-Safe Dictionary Extraction`
- `7. String Validation`
- `8. SHA256 Password Hashing with Salt`
- `9. UIViewController Navigation Helpers`
- `10. UIView Visual Effects (IBDesignable)`
- `11. Keyboard Handling — Animated Layout Shift`
- `12. UITextField Real-Time Formatting`
- `13. UIImage Processing`
- `14. Animation Patterns`
- `15. SwiftUI Core Recipes`
- `16. Async/Await Wrapper for Legacy Callbacks`
- `Key Rules`

## 2. Reusable NumberFormatter (Critical for scroll performance)

```swift
// Creating NumberFormatter per cell causes visible scroll lag — use a static lazy
class AppFormatters {
    static var threeDecimals: NumberFormatter = {
        let f = NumberFormatter()
        f.decimalSeparator = "."
        f.maximumFractionDigits = 3
        return f  // static vars are automatically lazy
    }()
}
extension String.StringInterpolation {
    mutating func appendInterpolation(_ v: Double) {
        appendLiteral(AppFormatters.threeDecimals.string(from: v as NSNumber) ?? "")
    }
}
```

---

## 3. ISO 8601 Date Handling

```swift
extension Formatter {
    static let iso8601: DateFormatter = {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .iso8601)
        f.locale   = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZZZZZ"
        return f
    }()
}
extension Date {
    var iso8601String: String { Formatter.iso8601.string(from: self) }
    init?(iso8601String: String) {
        guard let d = Formatter.iso8601.date(from: iso8601String) else { return nil }
        self = d
    }
}
```

---

## 4. Encodable/Decodable Universal Extensions

```swift
extension Encodable {
    var asJSONData: Data?            { try? JSONEncoder().encode(self) }
    var asJSONString: String?        { asJSONData.flatMap { String(data: $0, encoding: .utf8) } }
    var asDictionary: [String: Any]? {
        guard let d = asJSONData else { return nil }
        return (try? JSONSerialization.jsonObject(with: d)).flatMap { $0 as? [String: Any] }
    }
}
extension Decodable {
    init?(data: Data) {
        guard let v = try? JSONDecoder().decode(Self.self, from: data) else { return nil }
        self = v
    }
    init?(dict: [String: Any]) {
        guard let d = try? JSONSerialization.data(withJSONObject: dict) else { return nil }
        self.init(data: d)
    }
}
```

---

## 5. Custom Decoder — Handle API Type Mismatches

Server sends `age` as `"30"` (String) but Swift expects `Int`:

```swift
struct User: Codable {
    var name: String
    var age: Int?

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        name = try c.decode(String.self, forKey: .name)
        do {
            age = try c.decode(Int.self, forKey: .age)
        } catch DecodingError.typeMismatch {
            age = Int(try c.decode(String.self, forKey: .age))
        }
    }
    // Remap JSON keys to Swift names
    enum CodingKeys: String, CodingKey {
        case name = "firstName"
        case age
    }
}
```

---

## 6. Type-Safe Dictionary Extraction

```swift
extension Dictionary where Key: ExpressibleByStringLiteral {
    func getInt(_ key: String, defVal: Int? = nil) -> Int? {
        let val = self[key as! Key]
        if val == nil { return defVal }
        if let i = val as? Int    { return i }
        if let d = val as? Double { return Int(exactly: d.rounded()) }
        if let s = val as? String { return Int(s) ?? defVal }
        return defVal
    }
    func getString(_ key: String, defVal: String? = nil) -> String? {
        (self[key as! Key] as? String)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? defVal
    }
    func getBool(_ key: String, defVal: Bool? = nil) -> Bool? {
        let v = self[key as! Key]; if v == nil { return defVal }
        if let b = v as? Bool { return b }
        if let i = v as? Int  { return i != 0 }
        if let s = v as? String {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            if t == "true" || t == "yes"  { return true }
            if t == "false" || t == "no"  { return false }
        }
        return defVal
    }
}
// Handles "30", 30, 30.0 — all return Int(30)
// Handles "yes", "true", 1 — all return Bool(true)
```

---

## 7. String Validation

```swift
extension StringProtocol {
    var isValidEmail: Bool {
        NSPredicate(format: "SELF MATCHES %@",
            "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}")
            .evaluate(with: self)
    }
    var isValidName: Bool {
        let allowed = NSCharacterSet.letters
            .union(.whitespaces)
            .union(CharacterSet(charactersIn: ".-"))
        return rangeOfCharacter(from: allowed.inverted) == nil
    }
    var containsOnlyDigits: Bool {
        rangeOfCharacter(from: NSCharacterSet.decimalDigits.inverted) == nil
    }
    // Parse natural-language date strings ("Jan 15", "15/01/2024", etc.)
    var asDate: Date? {
        let range = NSRange(location: 0, length: count)
        return try? NSDataDetector(
            types: NSTextCheckingResult.CheckingType.date.rawValue)
            .matches(in: self as! String, range: range)
            .compactMap(\.date).first
    }
}
```

---

## 8. SHA256 Password Hashing with Salt

```swift
import CryptoKit
extension Data {
    var sha256: Data { Data(SHA256.hash(data: self).map { $0 as UInt8 }) }
}
extension String {
    var sha256: Data? { data(using: .utf8)?.sha256 }
}
// Always salt before hashing
let L = "LEFT_SALT"; let R = "RIGHT_SALT"  // compile-time constants, never change
let hash = "\(L)\(password)\(R)".sha256
// Send hash to server — server adds its own salt and hashes again
```

---

## 9. UIViewController Navigation Helpers

```swift
extension UIViewController {
    @IBAction func goBack() {
        view.endEditing(true)
        if let nc = navigationController, nc.viewControllers.count >= 2 {
            nc.popViewController(animated: true)
        } else {
            dismiss(animated: true)
        }
    }
}
extension UIWindow {
    func replaceRootViewController(with vc: UIViewController) {
        rootViewController = vc; makeKeyAndVisible()
    }
    static func replaceMainRoot(with vc: UIViewController) -> Bool {
        var w: UIWindow?
        if #available(iOS 13, *) {
            w = UIApplication.shared.connectedScenes
                .filter { $0.activationState == .foregroundActive }
                .compactMap { $0 as? UIWindowScene }
                .first?.windows.first(where: { $0.isKeyWindow })
        } else {
            w = (UIApplication.shared.delegate as? AppDelegate)?.window
        }
        w?.replaceRootViewController(with: vc); return w != nil
    }
}
// Remove specific VCs from navigation stack (post-purchase cleanup)
extension UINavigationController {
    func removeElements<T: UIViewController>(of type: T.Type) {
        viewControllers = viewControllers.filter { !($0 is T) }
    }
}
```

---

## 10. UIView Visual Effects (IBDesignable)

```swift
extension UIView {
    @IBInspectable var cornerRadius: CGFloat {
        set { layer.cornerRadius = newValue } get { layer.cornerRadius }
    }
    @IBInspectable var borderWidth: CGFloat {
        set { layer.borderWidth = newValue }  get { layer.borderWidth }
    }
    @IBInspectable var borderColor: UIColor? {
        set { layer.borderColor = newValue?.cgColor }
        get { layer.borderColor.map { UIColor(cgColor: $0) } }
    }
    @IBInspectable var dropShadow: Bool {
        set { if newValue { updateShadow() } else { layer.shadowOpacity = 0 } }
        get { layer.shadowOpacity > 0 }
    }
    func updateShadow() {
        layer.shadowColor   = UIColor.black.cgColor
        layer.shadowOpacity = 0.5; layer.shadowRadius = 4; layer.shadowOffset = .zero
        layer.shadowPath    = UIBezierPath(roundedRect: bounds,
                                           cornerRadius: layer.cornerRadius).cgPath
        layer.shouldRasterize = true; layer.rasterizationScale = UIScreen.main.scale
    }
    // Call in viewDidLayoutSubviews — shadow paths go stale after rotation
    func updateShadows() {
        if dropShadow { updateShadow() }
        subviews.forEach { $0.updateShadows() }
    }
}
```

---

## 11. Keyboard Handling — Animated Layout Shift

```swift
class FormVC: UIViewController {
    @IBOutlet weak var bottomConstraint: NSLayoutConstraint!

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        NotificationCenter.default.addObserver(self,
            selector: #selector(kbShow), name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.addObserver(self,
            selector: #selector(kbHide), name: UIResponder.keyboardWillHideNotification, object: nil)
    }
    override func viewDidDisappear(_ animated: Bool) {
        NotificationCenter.default.removeObserver(self,
            name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.removeObserver(self,
            name: UIResponder.keyboardWillHideNotification, object: nil)
        super.viewDidDisappear(animated)
    }
    @objc func kbShow(_ n: NSNotification) {
        guard let h = (n.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? NSValue)?
            .cgRectValue.size.height else { return }
        bottomConstraint.constant = h
        UIView.animate(withDuration: 0.3) { self.view.layoutIfNeeded() }
    }
    @objc func kbHide() {
        bottomConstraint.constant = 0
        UIView.animate(withDuration: 0.3) { self.view.layoutIfNeeded() }
    }
}
```

---

## 12. UITextField Real-Time Formatting

```swift
// Rule: always allow empty string (backspace) before any other check
// Rule: set textField.text inside DispatchQueue.main.async — change hasn't happened yet

// Credit card number: group by 4
extension String {
    func groupBy(_ n: Int = 4, sep: String = " ") -> String {
        guard count > n else { return self }
        let i = index(startIndex, offsetBy: n)
        return String(self[..<i]) + sep + String(self[i...]).groupBy(n, sep: sep)
    }
}
func cardField(_ tf: UITextField,
               shouldChange range: NSRange, replacement s: String) -> Bool {
    if s.isEmpty { return true }
    guard let text = tf.text, let r = Range(range, in: text) else { return true }
    let digits = text.replacingCharacters(in: r, with: s).filter("0123456789".contains)
    DispatchQueue.main.async { tf.text = digits.groupBy() }
    return true
}

// Emoji blocker
extension Character {
    var isEmoji: Bool {
        guard let s = unicodeScalars.first else { return false }
        return s.properties.isEmoji && (unicodeScalars.count > 1 || s.value > 0x238C)
    }
}
extension String {
    var containsEmoji: Bool { contains { $0.isEmoji } }
}
// In delegate: if string.containsEmoji && !string.isEmpty { return false }
```

---

## 13. UIImage Processing

```swift
extension UIImage {
    func resized(maxSize: CGFloat) -> UIImage? {
        let scale = maxSize / max(size.width, size.height)
        let s = CGSize(width: size.width * scale, height: size.height * scale)
        UIGraphicsBeginImageContext(s)
        draw(in: CGRect(origin: .zero, size: s))
        let r = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext(); return r
    }
    func downscaled(maxSize: CGFloat) -> UIImage? {
        max(size.width, size.height) > maxSize ? resized(maxSize: maxSize) : self
    }
    var squared: UIImage? {
        guard let cg = cgImage else { return nil }
        let ctx = UIImage(cgImage: cg); let s = ctx.size
        let side = min(s.width, s.height)
        let rect = CGRect(x: (s.width-side)/2, y: (s.height-side)/2, width: side, height: side)
        guard let ref = ctx.cgImage?.cropping(to: rect) else { return nil }
        return UIImage(cgImage: ref, scale: scale, orientation: imageOrientation)
    }
    // One-line profile picture prep: square + max 512px
    func prepareProfilePicture() -> UIImage { squared?.downscaled(maxSize: 512) ?? self }

    // Merge overlay (alpha compositing)
    func merge(with top: UIImage, x: CGFloat = 0, y: CGFloat = 0) -> UIImage? {
        UIGraphicsBeginImageContext(size)
        draw(at: .zero); top.draw(at: CGPoint(x: x, y: y))
        let r = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext(); return r
    }
}
```

---

## 14. Animation Patterns

```swift
// Fade
extension UIView {
    func fadeIn(_ duration: TimeInterval = 0.3) {
        isHidden = false; alpha = 0
        UIView.animate(withDuration: duration) { self.alpha = 1 }
    }
    func fadeOut(_ duration: TimeInterval = 0.3, done: (() -> Void)? = nil) {
        UIView.animate(withDuration: duration, animations: { self.alpha = 0 }) { _ in
            self.isHidden = true; done?()
        }
    }
}

// Parallax: lerp formula — final = from*(1-p) + to*p
func lerp(from: CGFloat, to: CGFloat, progress p: CGFloat) -> CGFloat { from*(1-p) + to*p }
// In scrollViewDidScroll: let p = max(0,min(1, contentOffset.y/280))
// headerHeight.constant = lerp(from:180, to:40, progress:p)
```

---

## 15. SwiftUI Core Recipes

```swift
// Reusable ViewModifier
struct HeaderStyle: ViewModifier {
    func body(content: Content) -> some View {
        content.font(.system(size: 20, weight: .bold))
               .foregroundColor(Color(UIColor.darkText)).lineLimit(1)
    }
}
extension Text { func styleAsHeader() -> some View { modifier(HeaderStyle()) } }

// @Binding + ObservableObject (shared state across child views)
class LoginVM: ObservableObject {
    @Published var login = ""; @Published var password = ""
}
struct LoginScreen: View {
    @ObservedObject var vm = LoginVM()
    var canLogin: Bool { !vm.login.isEmpty && !vm.password.isEmpty }
    var body: some View {
        VStack {
            TextField("Login", text: $vm.login)
            SecureField("Password", text: $vm.password)
            Button("Login") { }.disabled(!canLogin)
        }
    }
}

// Wrap UIKit view in SwiftUI
struct MapWrapper: UIViewRepresentable {
    func makeUIView(context: Context) -> MKMapView { MKMapView() }
    func updateUIView(_ v: MKMapView, context: Context) {}
}

// Use LazyVStack inside ScrollView for long lists (VStack renders all items at once)
ScrollView { LazyVStack { ForEach(items, id: \.id) { ItemRow($0) } } }
```

---

## 16. Async/Await Wrapper for Legacy Callbacks

```swift
// Convert any completion-handler function to async throws
func downloadAsync(url: URL) async throws -> Data {
    try await withUnsafeThrowingContinuation { continuation in
        URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error { continuation.resume(throwing: error); return }
            if let data  = data  { continuation.resume(returning: data);  return }
        }.resume()
    }
}
// Usage
Task {
    do {
        let data = try await downloadAsync(url: url)
        await MainActor.run { imageView.image = UIImage(data: data) }
    } catch { print(error) }
}
```

---

## Key Rules

- `Int` cents for prices, never `Double` — floating point loses fractions silently
- Static lazy `NumberFormatter` — creating per cell scroll is visibly slow
- Always allow `string.isEmpty` first in `shouldChangeCharacters` — backspace must work
- Set `textField.text` in `DispatchQueue.main.async` — the change hasn't applied yet
- Call `updateShadows()` from `viewDidLayoutSubviews` — shadow paths go stale after rotation
- Add `safeAreaInsets.top` to hero destination Y — nav bar absent during `prepare(for:segue:)`
- `@onChange` immediately after control, before style modifiers — modifiers return `View`, losing type
- `LazyVStack` not `VStack` in `ScrollView` — VStack renders all items at once
- `@Binding` for shared state, `@State` for local-only state
- Salt passwords before hashing — prevents cross-service hash correlation
