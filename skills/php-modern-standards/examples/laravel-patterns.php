<?php

declare(strict_types=1);

/**
 * Laravel-Specific Patterns
 *
 * Demonstrates Laravel best practices following Spatie guidelines and modern conventions.
 */

namespace App\Examples\Laravel;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\ValidationException;

// ============================================================================
// ELOQUENT MODELS (Spatie Conventions)
// ============================================================================

/**
 * User model with proper type hints and conventions.
 */
final class User extends Model
{
    // camelCase for non-public-facing strings
    protected $table = 'users';

    // Mass assignment protection
    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    // Proper casting (no docblocks needed)
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'is_active' => 'boolean',
        ];
    }

    // Relationships with proper return types
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }

    public function profile(): HasOne
    {
        return $this->hasOne(Profile::class);
    }

    // Accessor with proper type hint
    public function getFullNameAttribute(): string
    {
        return "{$this->first_name} {$this->last_name}";
    }

    // Mutator with proper type hint
    public function setEmailAttribute(string $value): void
    {
        $this->attributes['email'] = strtolower($value);
    }

    // Scope with proper type hint
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}

final class Post extends Model
{
    protected $fillable = [
        'title',
        'slug',
        'body',
        'user_id',
        'published_at',
    ];

    protected function casts(): array
    {
        return [
            'published_at' => 'datetime',
            'is_featured' => 'boolean',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    // Generate slug from title
    public static function boot(): void
    {
        parent::boot();

        static::creating(function (self $post): void {
            if (empty($post->slug)) {
                $post->slug = \Str::slug($post->title);
            }
        });
    }
}

// ============================================================================
// CONTROLLERS (Spatie Conventions)
// ============================================================================

/**
 * Plural resource names.
 * RESTful actions: index, show, create, store, edit, update, destroy.
 */
final class PostsController
{
    /**
     * Display a listing of posts.
     */
    public function index(): Response
    {
        // ✓ CORRECT: Use specific query methods
        $posts = Post::query()
            ->with('user')
            ->where('is_published', true)
            ->latest()
            ->paginate(15);

        return response()->json([
            'data' => $posts,
        ]);
    }

    /**
     * Display the specified post.
     */
    public function show(Post $post): Response
    {
        // Route model binding handles finding the post
        return response()->json([
            'data' => $post->load('user', 'comments'),
        ]);
    }

    /**
     * Store a newly created post.
     */
    public function store(StorePostRequest $request): Response
    {
        // Request validation happens in FormRequest
        $post = Post::create($request->validated());

        return response()->json([
            'data' => $post,
        ], 201);
    }

    /**
     * Update the specified post.
     */
    public function update(UpdatePostRequest $request, Post $post): Response
    {
        $post->update($request->validated());

        return response()->json([
            'data' => $post,
        ]);
    }

    /**
     * Remove the specified post.
     */
    public function destroy(Post $post): Response
    {
        $post->delete();

        return response()->json(null, 204);
    }
}

/**
 * Single resource controller (singular name).
 */
final class ProfileController
{
    public function show(): Response
    {
        $user = auth()->user();

        return response()->json([
            'data' => $user->profile,
        ]);
    }

    public function update(UpdateProfileRequest $request): Response
    {
        $user = auth()->user();
        $user->profile->update($request->validated());

        return response()->json([
            'data' => $user->profile,
        ]);
    }
}

// ============================================================================
// FORM REQUESTS (Validation)
// ============================================================================

final class StorePostRequest extends \Illuminate\Foundation\Http\FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return $this->user()->can('create', Post::class);
    }

    /**
     * Get the validation rules that apply to the request.
     */
    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'body' => ['required', 'string'],
            'published_at' => ['nullable', 'date', 'after:now'],
            'is_featured' => ['boolean'],
            'tags' => ['array'],
            'tags.*' => ['integer', 'exists:tags,id'],
        ];
    }

    /**
     * Get custom messages for validator errors.
     */
    public function messages(): array
    {
        return [
            'title.required' => 'The post title is required.',
            'title.max' => 'The post title cannot exceed 255 characters.',
            'body.required' => 'The post body is required.',
            'tags.*.exists' => 'One or more tags do not exist.',
        ];
    }

    /**
     * Prepare the data for validation.
     */
    protected function prepareForValidation(): void
    {
        $this->merge([
            'slug' => \Str::slug($this->title),
        ]);
    }
}

final class UpdatePostRequest extends \Illuminate\Foundation\Http\FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('update', $this->route('post'));
    }

    public function rules(): array
    {
        return [
            'title' => ['sometimes', 'string', 'max:255'],
            'body' => ['sometimes', 'string'],
            'published_at' => ['nullable', 'date'],
            'is_featured' => ['boolean'],
        ];
    }
}

// ============================================================================
// ROUTES (Spatie Conventions)
// ============================================================================

/**
 * In routes/api.php:
 *
 * use App\Http\Controllers\PostsController;
 * use App\Http\Controllers\ProfileController;
 *
 * // URLs: kebab-case
 * // Route names: camelCase
 * // Parameters: camelCase
 *
 * // Resource routes (plural)
 * Route::get('/posts', [PostsController::class, 'index'])
 *     ->name('posts.index');
 *
 * Route::get('/posts/{post}', [PostsController::class, 'show'])
 *     ->name('posts.show');
 *
 * Route::post('/posts', [PostsController::class, 'store'])
 *     ->name('posts.store');
 *
 * Route::put('/posts/{post}', [PostsController::class, 'update'])
 *     ->name('posts.update');
 *
 * Route::delete('/posts/{post}', [PostsController::class, 'destroy'])
 *     ->name('posts.destroy');
 *
 * // Or use resource helper
 * Route::apiResource('posts', PostsController::class);
 *
 * // Single resource (singular)
 * Route::get('/profile', [ProfileController::class, 'show'])
 *     ->name('profile.show');
 *
 * Route::put('/profile', [ProfileController::class, 'update'])
 *     ->name('profile.update');
 *
 * // Nested resources
 * Route::get('/posts/{post}/comments', [CommentsController::class, 'index'])
 *     ->name('posts.comments.index');
 */

// ============================================================================
// SERVICES (Business Logic)
// ============================================================================

/**
 * Service class for complex business logic.
 * Keep controllers thin, move logic to services.
 */
final readonly class PostPublishingService
{
    public function __construct(
        private PostRepository $postRepository,
        private NotificationService $notificationService,
    ) {
    }

    public function publish(Post $post): void
    {
        // Validate post is ready for publishing
        if (empty($post->title) || empty($post->body)) {
            throw new \DomainException('Post must have title and body to be published');
        }

        if ($post->is_published) {
            throw new \DomainException('Post is already published');
        }

        // Update post status
        $post->update([
            'is_published' => true,
            'published_at' => now(),
        ]);

        // Send notifications
        $this->notificationService->notifyFollowers($post->user, $post);

        // Dispatch events
        event(new PostPublished($post));
    }

    public function unpublish(Post $post): void
    {
        if (!$post->is_published) {
            throw new \DomainException('Post is not published');
        }

        $post->update([
            'is_published' => false,
            'published_at' => null,
        ]);

        event(new PostUnpublished($post));
    }
}

// ============================================================================
// REPOSITORIES (Data Access Layer)
// ============================================================================

/**
 * Repository pattern for complex queries and data access.
 */
interface PostRepository
{
    public function findById(int $id): ?Post;
    public function findBySlug(string $slug): ?Post;
    public function findPublished(int $limit = 10): \Illuminate\Database\Eloquent\Collection;
    public function search(string $query): \Illuminate\Database\Eloquent\Collection;
}

final readonly class EloquentPostRepository implements PostRepository
{
    public function findById(int $id): ?Post
    {
        return Post::find($id);
    }

    public function findBySlug(string $slug): ?Post
    {
        return Post::where('slug', $slug)->first();
    }

    public function findPublished(int $limit = 10): \Illuminate\Database\Eloquent\Collection
    {
        return Post::query()
            ->where('is_published', true)
            ->where('published_at', '<=', now())
            ->latest('published_at')
            ->limit($limit)
            ->get();
    }

    public function search(string $query): \Illuminate\Database\Eloquent\Collection
    {
        return Post::query()
            ->where('is_published', true)
            ->where(function ($q) use ($query): void {
                $q->where('title', 'LIKE', "%$query%")
                    ->orWhere('body', 'LIKE', "%$query%");
            })
            ->latest()
            ->get();
    }
}

// ============================================================================
// EVENTS AND LISTENERS
// ============================================================================

final readonly class PostPublished
{
    public function __construct(
        public Post $post,
    ) {
    }
}

final readonly class SendPostPublishedNotification
{
    public function __construct(
        private NotificationService $notificationService,
    ) {
    }

    public function handle(PostPublished $event): void
    {
        $this->notificationService->notifyFollowers(
            $event->post->user,
            $event->post
        );
    }
}

// ============================================================================
// ACTIONS (Single-Purpose Classes)
// ============================================================================

/**
 * Action classes for single, focused operations.
 * Use when operation is complex enough to warrant its own class.
 */
final readonly class CreatePostAction
{
    public function __construct(
        private PostRepository $postRepository,
    ) {
    }

    public function execute(User $user, array $data): Post
    {
        // Validate
        $validator = Validator::make($data, [
            'title' => ['required', 'string', 'max:255'],
            'body' => ['required', 'string'],
        ]);

        if ($validator->fails()) {
            throw new ValidationException($validator);
        }

        // Create post
        return $user->posts()->create([
            'title' => $data['title'],
            'body' => $data['body'],
            'slug' => \Str::slug($data['title']),
        ]);
    }
}

// ============================================================================
// QUERY BUILDERS (Complex Queries)
// ============================================================================

/**
 * Custom query builder for complex filtering.
 */
final class PostQueryBuilder extends \Illuminate\Database\Eloquent\Builder
{
    public function published(): self
    {
        return $this->where('is_published', true)
            ->where('published_at', '<=', now());
    }

    public function featured(): self
    {
        return $this->where('is_featured', true);
    }

    public function byAuthor(User $user): self
    {
        return $this->where('user_id', $user->id);
    }

    public function inDateRange(\DateTimeInterface $start, \DateTimeInterface $end): self
    {
        return $this->whereBetween('published_at', [$start, $end]);
    }

    public function withStats(): self
    {
        return $this->withCount('comments')
            ->withCount('likes');
    }
}

// Add to Post model:
// public function newEloquentBuilder($query): PostQueryBuilder
// {
//     return new PostQueryBuilder($query);
// }

// Usage:
// $posts = Post::query()
//     ->published()
//     ->featured()
//     ->withStats()
//     ->latest()
//     ->get();

// ============================================================================
// MIDDLEWARE
// ============================================================================

final readonly class EnsureUserIsActive
{
    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, \Closure $next): mixed
    {
        $user = $request->user();

        if ($user && !$user->is_active) {
            return response()->json([
                'message' => 'Your account is not active.',
            ], 403);
        }

        return $next($request);
    }
}

// ============================================================================
// RESOURCES (API Transformers)
// ============================================================================

final class PostResource extends \Illuminate\Http\Resources\Json\JsonResource
{
    /**
     * Transform the resource into an array.
     */
    public function toArray($request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'slug' => $this->slug,
            'body' => $this->body,
            'is_published' => $this->is_published,
            'published_at' => $this->published_at?->toISOString(),
            'author' => new UserResource($this->whenLoaded('user')),
            'comments_count' => $this->when(
                $this->relationLoaded('comments'),
                fn () => $this->comments->count()
            ),
            'created_at' => $this->created_at->toISOString(),
            'updated_at' => $this->updated_at->toISOString(),
        ];
    }
}

final class UserResource extends \Illuminate\Http\Resources\Json\JsonResource
{
    public function toArray($request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->when(
                $request->user()?->id === $this->id,
                $this->email
            ),
            'created_at' => $this->created_at->toISOString(),
        ];
    }
}

// ============================================================================
// JOBS (Queued Tasks)
// ============================================================================

final readonly class ProcessPostPublication implements \Illuminate\Contracts\Queue\ShouldQueue
{
    use \Illuminate\Bus\Queueable;
    use \Illuminate\Queue\InteractsWithQueue;
    use \Illuminate\Queue\SerializesModels;

    public function __construct(
        private Post $post,
    ) {
    }

    /**
     * Execute the job.
     */
    public function handle(NotificationService $notificationService): void
    {
        // Send notifications
        $notificationService->notifyFollowers($this->post->user, $this->post);

        // Update search index
        // ProcessSearchIndexing::dispatch($this->post);

        // Other background tasks...
    }

    /**
     * Handle a job failure.
     */
    public function failed(\Throwable $exception): void
    {
        // Log the failure
        \Log::error('Post publication processing failed', [
            'post_id' => $this->post->id,
            'exception' => $exception->getMessage(),
        ]);
    }
}

// ============================================================================
// POLICIES (Authorization)
// ============================================================================

final readonly class PostPolicy
{
    /**
     * Determine if the user can view any posts.
     */
    public function viewAny(?User $user): bool
    {
        return true;
    }

    /**
     * Determine if the user can view the post.
     */
    public function view(?User $user, Post $post): bool
    {
        return $post->is_published || $user?->id === $post->user_id;
    }

    /**
     * Determine if the user can create posts.
     */
    public function create(User $user): bool
    {
        return $user->is_active;
    }

    /**
     * Determine if the user can update the post.
     */
    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }

    /**
     * Determine if the user can delete the post.
     */
    public function delete(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }
}
