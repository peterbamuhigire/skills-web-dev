<?php

declare(strict_types=1);

/**
 * Modern PHP Patterns Examples
 *
 * Demonstrates modern PHP 8+ features, patterns, and best practices.
 */

namespace App\Examples;

// ============================================================================
// ENUMS (PHP 8.1+)
// ============================================================================

enum OrderStatus: string
{
    case Pending = 'pending';
    case Processing = 'processing';
    case Shipped = 'shipped';
    case Delivered = 'delivered';
    case Cancelled = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::Pending => 'Pending Payment',
            self::Processing => 'Processing Order',
            self::Shipped => 'Shipped',
            self::Delivered => 'Delivered',
            self::Cancelled => 'Cancelled',
        };
    }

    public function canTransitionTo(self $newStatus): bool
    {
        return match ($this) {
            self::Pending => in_array($newStatus, [self::Processing, self::Cancelled], true),
            self::Processing => in_array($newStatus, [self::Shipped, self::Cancelled], true),
            self::Shipped => in_array($newStatus, [self::Delivered, self::Cancelled], true),
            self::Delivered => false,
            self::Cancelled => false,
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::Pending => 'yellow',
            self::Processing => 'blue',
            self::Shipped => 'purple',
            self::Delivered => 'green',
            self::Cancelled => 'red',
        };
    }
}

// ============================================================================
// VALUE OBJECTS (Readonly Classes)
// ============================================================================

final readonly class Money
{
    public function __construct(
        public float $amount,
        public string $currency = 'USD',
    ) {
        if ($amount < 0) {
            throw new \InvalidArgumentException('Amount cannot be negative');
        }

        if (strlen($currency) !== 3) {
            throw new \InvalidArgumentException('Currency must be 3-letter ISO code');
        }
    }

    public function add(self $other): self
    {
        $this->assertSameCurrency($other);

        return new self($this->amount + $other->amount, $this->currency);
    }

    public function subtract(self $other): self
    {
        $this->assertSameCurrency($other);

        return new self($this->amount - $other->amount, $this->currency);
    }

    public function multiply(float $multiplier): self
    {
        return new self($this->amount * $multiplier, $this->currency);
    }

    public function isGreaterThan(self $other): bool
    {
        $this->assertSameCurrency($other);

        return $this->amount > $other->amount;
    }

    public function format(): string
    {
        return match ($this->currency) {
            'USD' => '$' . number_format($this->amount, 2),
            'EUR' => '€' . number_format($this->amount, 2),
            'GBP' => '£' . number_format($this->amount, 2),
            default => $this->currency . ' ' . number_format($this->amount, 2),
        };
    }

    private function assertSameCurrency(self $other): void
    {
        if ($this->currency !== $other->currency) {
            throw new \InvalidArgumentException('Cannot operate on different currencies');
        }
    }
}

final readonly class Email
{
    public function __construct(
        public string $value,
    ) {
        if (!filter_var($value, FILTER_VALIDATE_EMAIL)) {
            throw new \InvalidArgumentException("Invalid email address: $value");
        }
    }

    public function domain(): string
    {
        return substr($this->value, strpos($this->value, '@') + 1);
    }

    public function localPart(): string
    {
        return substr($this->value, 0, strpos($this->value, '@'));
    }
}

// ============================================================================
// ENTITIES WITH CONSTRUCTOR PROPERTY PROMOTION
// ============================================================================

final class Order
{
    private OrderStatus $status;
    private \DateTimeImmutable $createdAt;
    private ?\DateTimeImmutable $completedAt = null;

    /** @var OrderItem[] */
    private array $items = [];

    public function __construct(
        private readonly int $id,
        private readonly int $customerId,
    ) {
        $this->status = OrderStatus::Pending;
        $this->createdAt = new \DateTimeImmutable();
    }

    public function addItem(OrderItem $item): void
    {
        $this->items[] = $item;
    }

    public function total(): Money
    {
        if (empty($this->items)) {
            return new Money(0);
        }

        $total = $this->items[0]->total();

        foreach (array_slice($this->items, 1) as $item) {
            $total = $total->add($item->total());
        }

        return $total;
    }

    public function updateStatus(OrderStatus $newStatus): void
    {
        if (!$this->status->canTransitionTo($newStatus)) {
            throw new \DomainException(
                "Cannot transition from {$this->status->value} to {$newStatus->value}"
            );
        }

        $this->status = $newStatus;

        if ($newStatus === OrderStatus::Delivered) {
            $this->completedAt = new \DateTimeImmutable();
        }
    }

    public function getId(): int
    {
        return $this->id;
    }

    public function getStatus(): OrderStatus
    {
        return $this->status;
    }

    public function getItems(): array
    {
        return $this->items;
    }
}

final readonly class OrderItem
{
    public function __construct(
        private int $productId,
        private string $productName,
        private Money $unitPrice,
        private int $quantity,
    ) {
        if ($quantity <= 0) {
            throw new \InvalidArgumentException('Quantity must be positive');
        }
    }

    public function total(): Money
    {
        return $this->unitPrice->multiply($this->quantity);
    }

    public function getProductId(): int
    {
        return $this->productId;
    }

    public function getProductName(): string
    {
        return $this->productName;
    }

    public function getQuantity(): int
    {
        return $this->quantity;
    }
}

// ============================================================================
// REPOSITORY PATTERN WITH GENERATORS
// ============================================================================

interface OrderRepository
{
    public function save(Order $order): void;
    public function findById(int $id): ?Order;
    public function findByCustomer(int $customerId): array;

    /**
     * Returns a generator for memory-efficient iteration over large datasets.
     *
     * @return \Generator<Order>
     */
    public function findAll(): \Generator;
}

final readonly class PdoOrderRepository implements OrderRepository
{
    public function __construct(
        private \PDO $pdo,
    ) {
    }

    public function save(Order $order): void
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO orders (id, customer_id, status, created_at)
             VALUES (:id, :customer_id, :status, :created_at)
             ON DUPLICATE KEY UPDATE status = :status'
        );

        $stmt->execute([
            'id' => $order->getId(),
            'customer_id' => $order->getId(),
            'status' => $order->getStatus()->value,
            'created_at' => (new \DateTimeImmutable())->format('Y-m-d H:i:s'),
        ]);

        // Save order items...
    }

    public function findById(int $id): ?Order
    {
        $stmt = $this->pdo->prepare('SELECT * FROM orders WHERE id = ?');
        $stmt->execute([$id]);

        $row = $stmt->fetch(\PDO::FETCH_ASSOC);

        return $row ? $this->hydrate($row) : null;
    }

    public function findByCustomer(int $customerId): array
    {
        $stmt = $this->pdo->prepare('SELECT * FROM orders WHERE customer_id = ?');
        $stmt->execute([$customerId]);

        return array_map(
            fn (array $row) => $this->hydrate($row),
            $stmt->fetchAll(\PDO::FETCH_ASSOC)
        );
    }

    /**
     * Memory-efficient iteration using generator.
     */
    public function findAll(): \Generator
    {
        $stmt = $this->pdo->query('SELECT * FROM orders');

        while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
            yield $this->hydrate($row);
        }
    }

    private function hydrate(array $row): Order
    {
        $order = new Order(
            id: (int) $row['id'],
            customerId: (int) $row['customer_id']
        );

        // Load order items and set status...

        return $order;
    }
}

// ============================================================================
// SERVICE LAYER WITH MATCH EXPRESSIONS
// ============================================================================

final readonly class OrderService
{
    public function __construct(
        private OrderRepository $orderRepository,
        private PaymentGateway $paymentGateway,
        private EmailService $emailService,
    ) {
    }

    public function createOrder(int $customerId, array $items): Order
    {
        $order = new Order($this->generateOrderId(), $customerId);

        foreach ($items as $item) {
            $order->addItem(new OrderItem(
                productId: $item['product_id'],
                productName: $item['product_name'],
                unitPrice: new Money($item['price']),
                quantity: $item['quantity']
            ));
        }

        $this->orderRepository->save($order);

        return $order;
    }

    public function processPayment(Order $order, string $paymentMethod): PaymentResult
    {
        $result = $this->paymentGateway->charge(
            amount: $order->total(),
            method: $paymentMethod
        );

        // Match expression for cleaner state handling
        $newStatus = match ($result->status) {
            PaymentResultStatus::Success => OrderStatus::Processing,
            PaymentResultStatus::Failed => OrderStatus::Cancelled,
            PaymentResultStatus::Pending => OrderStatus::Pending,
        };

        $order->updateStatus($newStatus);
        $this->orderRepository->save($order);

        // Send notification based on result
        $this->sendNotification($order, $result);

        return $result;
    }

    private function sendNotification(Order $order, PaymentResult $result): void
    {
        $template = match ($result->status) {
            PaymentResultStatus::Success => 'order.payment_success',
            PaymentResultStatus::Failed => 'order.payment_failed',
            PaymentResultStatus::Pending => 'order.payment_pending',
        };

        $this->emailService->send($template, [
            'order' => $order,
            'result' => $result,
        ]);
    }

    private function generateOrderId(): int
    {
        // Implementation...
        return random_int(100000, 999999);
    }
}

// ============================================================================
// UNION TYPES (PHP 8.0+)
// ============================================================================

final readonly class PaymentGateway
{
    public function charge(Money $amount, string $method): PaymentResult
    {
        // Implementation...
        return new PaymentResult(
            status: PaymentResultStatus::Success,
            transactionId: 'txn_' . bin2hex(random_bytes(8))
        );
    }

    /**
     * Union type: accepts int or string ID.
     */
    public function refund(int|string $transactionId, Money $amount): PaymentResult
    {
        $id = is_int($transactionId) ? (string) $transactionId : $transactionId;

        // Implementation...
        return new PaymentResult(
            status: PaymentResultStatus::Success,
            transactionId: $id
        );
    }
}

enum PaymentResultStatus: string
{
    case Success = 'success';
    case Failed = 'failed';
    case Pending = 'pending';
}

final readonly class PaymentResult
{
    public function __construct(
        public PaymentResultStatus $status,
        public string $transactionId,
        public ?string $errorMessage = null,
    ) {
    }
}

// ============================================================================
// NAMED ARGUMENTS (PHP 8.0+)
// ============================================================================

final readonly class EmailService
{
    public function send(
        string $template,
        array $data = [],
        ?string $to = null,
        ?string $from = null,
        bool $trackOpens = true,
        bool $trackClicks = true,
    ): void {
        // Implementation...
    }
}

// Usage with named arguments
$emailService = new EmailService();
$emailService->send(
    template: 'welcome',
    data: ['name' => 'John'],
    to: 'user@example.com',
    trackOpens: true,
    trackClicks: false
);

// ============================================================================
// NULLSAFE OPERATOR (PHP 8.0+)
// ============================================================================

final readonly class Customer
{
    public function __construct(
        private int $id,
        private string $name,
        private ?Address $address = null,
    ) {
    }

    public function getAddress(): ?Address
    {
        return $this->address;
    }
}

final readonly class Address
{
    public function __construct(
        private string $street,
        private string $city,
        private string $country,
    ) {
    }

    public function getCountry(): string
    {
        return $this->country;
    }
}

// Nullsafe operator example
function getCustomerCountry(Customer $customer): ?string
{
    // Without nullsafe operator (verbose)
    // if ($customer->getAddress() !== null) {
    //     return $customer->getAddress()->getCountry();
    // }
    // return null;

    // With nullsafe operator (concise)
    return $customer->getAddress()?->getCountry();
}

// ============================================================================
// GENERATOR FOR LARGE DATASETS
// ============================================================================

final readonly class ReportGenerator
{
    public function __construct(
        private \PDO $pdo,
    ) {
    }

    /**
     * Processes large dataset without loading all into memory.
     *
     * @return \Generator<array>
     */
    public function generateSalesReport(\DateTimeImmutable $startDate, \DateTimeImmutable $endDate): \Generator
    {
        $stmt = $this->pdo->prepare(
            'SELECT * FROM orders WHERE created_at BETWEEN ? AND ?'
        );

        $stmt->execute([
            $startDate->format('Y-m-d'),
            $endDate->format('Y-m-d'),
        ]);

        // Yields one row at a time (memory-efficient)
        while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
            yield [
                'order_id' => $row['id'],
                'total' => $row['total'],
                'customer' => $row['customer_name'],
                'date' => $row['created_at'],
            ];
        }
    }
}

// Usage
$reportGenerator = new ReportGenerator($pdo);
$report = $reportGenerator->generateSalesReport(
    startDate: new \DateTimeImmutable('2026-01-01'),
    endDate: new \DateTimeImmutable('2026-01-31')
);

// Process one row at a time (low memory usage)
foreach ($report as $row) {
    // Process each row without loading entire dataset
    echo "Order {$row['order_id']}: {$row['total']}\n";
}

// ============================================================================
// ATTRIBUTES (PHP 8.0+)
// ============================================================================

#[\Attribute(\Attribute::TARGET_METHOD)]
final readonly class Route
{
    public function __construct(
        public string $path,
        public string $method = 'GET',
    ) {
    }
}

#[\Attribute(\Attribute::TARGET_CLASS)]
final readonly class Controller
{
    public function __construct(
        public string $prefix = '',
    ) {
    }
}

#[Controller(prefix: '/api/orders')]
final readonly class OrdersController
{
    #[Route('/api/orders', 'GET')]
    public function index(): array
    {
        return ['orders' => []];
    }

    #[Route('/api/orders/{id}', 'GET')]
    public function show(int $id): array
    {
        return ['order' => []];
    }

    #[Route('/api/orders', 'POST')]
    public function store(): array
    {
        return ['order' => []];
    }
}
