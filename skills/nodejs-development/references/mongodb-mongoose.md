# MongoDB / Mongoose — Deep Dive

## Connection and Configuration

```js
import mongoose from 'mongoose'

// Always allow override via env
await mongoose.connect(
  process.env.MONGO_URI || 'mongodb://localhost:27017/myapp',
  { useNewUrlParser: true, useCreateIndex: true }
)

mongoose.connection.on('error', err => {
  console.error('MongoDB error:', err)
  process.exit(1)
})

mongoose.connection.once('open', () => console.log('MongoDB connected'))
```

## Schema Design

```js
import cuid from 'cuid'
import { isURL, isEmail } from 'validator'

// URL validator factory (reusable)
function urlField(required = false) {
  return {
    type: String,
    required,
    validate: {
      validator: isURL,
      message: props => `${props.value} is not a valid URL`
    }
  }
}

const ProductSchema = new mongoose.Schema({
  _id:         { type: String, default: cuid },
  name:        { type: String, required: true, trim: true, maxlength: 200 },
  description: { type: String, trim: true },
  price:       { type: Number, required: true, min: 0 },
  img:         urlField(true),
  link:        urlField(),
  userId:      { type: String, required: true, index: true },
  tags:        { type: [String], index: true },
  status:      {
    type: String,
    enum: ['draft', 'active', 'archived'],
    default: 'draft',
    index: true
  }
}, {
  timestamps: true   // adds createdAt, updatedAt automatically
})

// Compound index
ProductSchema.index({ userId: 1, status: 1 })

const Product = mongoose.model('Product', ProductSchema)
```

## CRUD with Validation

```js
// Create
async function createProduct(data) {
  const product = new Product(data)
  return product.save()   // throws ValidationError on invalid data
}

// List with pagination
async function listProducts({ offset = 0, limit = 25, tag, status } = {}) {
  const filter = {}
  if (tag) filter.tags = tag
  if (status) filter.status = status
  return Product.find(filter)
    .skip(offset).limit(limit)
    .sort({ createdAt: -1 })
    .lean()   // returns plain objects, not Mongoose documents (faster)
}

// Get one
async function getProduct(id) {
  const product = await Product.findById(id)
  if (!product) throw new AppError('Not found', 'NOT_FOUND', 404)
  return product
}

// Update — ALWAYS fetch then save (triggers validation + hooks)
async function updateProduct(id, changes) {
  const product = await Product.findById(id)
  if (!product) throw new AppError('Not found', 'NOT_FOUND', 404)
  Object.assign(product, changes)
  return product.save()
  // NEVER use findByIdAndUpdate — bypasses validators and hooks
}

// Delete
async function deleteProduct(id) {
  const result = await Product.deleteOne({ _id: id })
  if (result.deletedCount === 0) throw new AppError('Not found', 'NOT_FOUND', 404)
}
```

## Relationships and Populate

```js
const OrderSchema = new mongoose.Schema({
  _id:         { type: String, default: cuid },
  buyerEmail:  {
    type: String, required: true,
    validate: { validator: isEmail, message: 'Invalid email' }
  },
  products:    [{ type: String, ref: 'Product', required: true }],  // array of IDs
  status:      {
    type: String,
    enum: ['CREATED', 'PENDING', 'COMPLETED'],
    default: 'CREATED'
  }
})

const Order = mongoose.model('Order', OrderSchema)

// Populate fills product IDs with full product objects
async function getOrder(id) {
  return Order.findById(id)
    .populate('products')   // replaces product IDs with Product documents
    .exec()
}

// Selective populate (only some fields)
await Order.findById(id)
  .populate('products', 'name price img')  // only these fields
  .exec()
```

## Mongoose Hooks (Middleware)

```js
// Pre-save hook
ProductSchema.pre('save', function(next) {
  this.name = this.name.trim()
  if (this.isNew) this.slug = slugify(this.name)
  next()
})

// Post-save hook (for side effects)
ProductSchema.post('save', async function(doc) {
  await SearchIndex.upsert(doc)
})

// Pre-delete cleanup
ProductSchema.pre('deleteOne', { document: true }, async function() {
  await Order.updateMany(
    { products: this._id },
    { $pull: { products: this._id } }
  )
})
```

## Query Patterns

```js
// Text search (requires text index)
ProductSchema.index({ name: 'text', description: 'text' })
await Product.find({ $text: { $search: 'blue shoes' } })
  .sort({ score: { $meta: 'textScore' } })

// Range queries
await Product.find({ price: { $gte: 10, $lte: 100 } })

// Array contains
await Product.find({ tags: { $in: ['shoe', 'sneaker'] } })

// Aggregation
const stats = await Product.aggregate([
  { $match: { status: 'active' } },
  { $group: {
    _id: '$userId',
    count: { $sum: 1 },
    avgPrice: { $avg: '$price' }
  }},
  { $sort: { count: -1 } }
])
```

## Error Handling

```js
import mongoose from 'mongoose'

function handleMongoError(err) {
  if (err.name === 'ValidationError') {
    const messages = Object.values(err.errors).map(e => e.message)
    return { status: 400, message: 'Validation failed', details: messages }
  }
  if (err.code === 11000) {  // duplicate key
    return { status: 409, message: 'Duplicate entry' }
  }
  if (err.name === 'CastError') {
    return { status: 400, message: `Invalid ${err.path}: ${err.value}` }
  }
  return { status: 500, message: 'Database error' }
}

// Express error middleware
app.use((err, req, res, next) => {
  if (err instanceof mongoose.Error) {
    const { status, message, details } = handleMongoError(err)
    return res.status(status).json({ error: message, details })
  }
  next(err)
})
```
