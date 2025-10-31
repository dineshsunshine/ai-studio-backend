# Token Consumption Integration Guide for Frontend

## Overview

The backend now controls all token costs. Frontend sends **operation name**, backend determines the cost and handles token deduction.

---

## Quick Start

### Step 1: Fetch Operation Costs (Optional - for displaying costs to users)

```javascript
// Get all operation costs when app loads
const response = await fetch('${API_BASE_URL}/api/v1/subscription/costs');
const data = await response.json();

console.log(data.costs);
// {
//   "text_to_image": 10,
//   "multi_modal": 20,
//   "multi_modal_light": 8,
//   "video_generation": 50,
//   "image_to_text": 5,
//   "text_to_text": 3
// }
```

---

### Step 2: Consume Tokens BEFORE AI Operation

**Important:** Call this endpoint **BEFORE** you trigger the actual AI operation.

```javascript
async function consumeTokens(operation, description) {
  const response = await fetch('${API_BASE_URL}/api/v1/subscription/consume', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}`
    },
    body: JSON.stringify({
      operation: operation,
      description: description  // Optional context
    })
  });

  const result = await response.json();
  return result;
}
```

---

## Operation Names

Use these exact operation names when calling `/consume`:

| Operation Name      | Used For                    | Cost (Tokens) |
|---------------------|----------------------------|---------------|
| `text_to_image`     | Model Manager (AI Generate) | 10            |
| `multi_modal`       | Look Creator (Full)         | 20            |
| `multi_modal_light` | Finishing Studio            | 8             |
| `video_generation`  | Video Content Generation    | 50            |
| `image_to_text`     | Image analysis              | 5             |
| `text_to_text`      | Copywriter                  | 3             |

---

## Integration Example: Model Generation

```javascript
async function generateModel(modelName, promptDetails) {
  try {
    // Step 1: Consume tokens FIRST
    const tokenResult = await consumeTokens(
      'text_to_image',
      `Generated model: ${modelName}`
    );

    // Step 2: Check if successful
    if (!tokenResult.success) {
      // Show upgrade modal or error
      showUpgradeModal(tokenResult.message, tokenResult.cost);
      return null;
    }

    // Step 3: Proceed with actual AI operation
    const modelResponse = await fetch('${API_BASE_URL}/api/v1/models/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userToken}`
      },
      body: formData
    });

    // Step 4: Update UI with remaining tokens
    updateTokenDisplay(tokenResult.availableTokens);

    return modelResponse;

  } catch (error) {
    console.error('Error:', error);
    showError('Failed to generate model');
  }
}
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "cost": 10,
  "availableTokens": 90,
  "consumedTokens": 10,
  "message": "Successfully consumed 10 tokens for 'text_to_image' operation."
}
```

### Insufficient Tokens Response
```json
{
  "success": false,
  "cost": 10,
  "availableTokens": 5,
  "consumedTokens": 95,
  "message": "Insufficient tokens. Operation 'text_to_image' costs 10 tokens but you have 5."
}
```

### Invalid Operation Error (400)
```json
{
  "detail": "Invalid operation: wrong_operation. Valid operations: ['text_to_image', 'multi_modal', 'multi_modal_light', 'video_generation', 'image_to_text', 'text_to_text']"
}
```

---

## Complete Integration Flow

```javascript
// 1. When app loads, fetch costs for display
async function initApp() {
  const costsResponse = await fetch('${API_BASE_URL}/api/v1/subscription/costs');
  const { costs } = await costsResponse.json();
  
  // Store costs globally or in state
  window.OPERATION_COSTS = costs;
}

// 2. Display cost to user BEFORE they click
function showGenerateButton() {
  const cost = window.OPERATION_COSTS['text_to_image'];
  return `Generate Model (${cost} tokens)`;
}

// 3. When user clicks, consume tokens first
async function onGenerateModelClick(modelData) {
  // Show loading state
  setLoading(true);

  // Consume tokens
  const result = await consumeTokens(
    'text_to_image',
    `Generate model: ${modelData.name}`
  );

  if (!result.success) {
    // Not enough tokens - show upgrade modal
    showUpgradeModal({
      requiredTokens: result.cost,
      availableTokens: result.availableTokens,
      shortfall: result.cost - result.availableTokens
    });
    setLoading(false);
    return;
  }

  // Tokens consumed successfully - proceed with AI operation
  try {
    const model = await actuallyGenerateModel(modelData);
    
    // Update token balance in UI
    updateTokenBalance(result.availableTokens);
    
    // Show success
    showSuccess(`Model created! ${result.availableTokens} tokens remaining.`);
    
  } catch (error) {
    // AI operation failed but tokens were already consumed
    // Consider refund logic or error handling
    showError('Generation failed. Please try again.');
  }

  setLoading(false);
}
```

---

## Displaying Costs in UI

### Example 1: Button with Cost
```javascript
<button onClick={handleGenerate}>
  Generate Model ({OPERATION_COSTS.text_to_image} tokens)
</button>
```

### Example 2: Check if user can afford before showing button
```javascript
function CanAffordButton({ operation, onClick, children }) {
  const cost = OPERATION_COSTS[operation];
  const { availableTokens } = useSubscription();
  
  const canAfford = availableTokens >= cost;
  
  return (
    <button 
      onClick={onClick} 
      disabled={!canAfford}
      className={!canAfford ? 'btn-disabled' : 'btn-primary'}
    >
      {children} ({cost} tokens)
      {!canAfford && ' - Insufficient tokens'}
    </button>
  );
}
```

### Example 3: Warning before action
```javascript
function showCostWarning(operation) {
  const cost = OPERATION_COSTS[operation];
  const { availableTokens } = getUserSubscription();
  
  if (availableTokens < cost) {
    return `You need ${cost} tokens but only have ${availableTokens}. Upgrade to continue.`;
  }
  return null;
}
```

---

## Error Handling

```javascript
async function safeConsumeTokens(operation, description) {
  try {
    const response = await fetch('${API_BASE_URL}/api/v1/subscription/consume', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}`
      },
      body: JSON.stringify({ operation, description })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to consume tokens');
    }

    return await response.json();

  } catch (error) {
    console.error('Token consumption error:', error);
    
    // Show user-friendly error
    showNotification({
      type: 'error',
      message: 'Unable to process tokens. Please try again or contact support.'
    });
    
    return { success: false };
  }
}
```

---

## Best Practices

### ✅ DO:
- **Always call `/consume` BEFORE the AI operation**
- **Display token costs to users upfront**
- **Handle insufficient tokens gracefully (show upgrade modal)**
- **Update token balance in UI after each operation**
- **Cache costs in memory (they don't change often)**

### ❌ DON'T:
- **Don't call AI operation before checking tokens**
- **Don't hardcode costs in frontend (use `/costs` endpoint)**
- **Don't assume operation will succeed after token consumption**
- **Don't forget to handle error cases**

---

## API Endpoints Summary

| Method | Endpoint                        | Auth Required | Purpose                          |
|--------|---------------------------------|---------------|----------------------------------|
| GET    | `/api/v1/subscription/costs`    | No            | Get all operation costs          |
| POST   | `/api/v1/subscription/consume`  | Yes           | Consume tokens for operation     |
| GET    | `/api/v1/subscription/info`     | Yes           | Get user's subscription & balance|
| GET    | `/api/v1/subscription/tiers`    | No            | Get all subscription tiers       |
| GET    | `/api/v1/subscription/history`  | Yes           | Get token transaction history    |

---

## Testing

### Test with cURL

```bash
# Get costs (no auth needed)
curl https://your-api.com/api/v1/subscription/costs

# Consume tokens (requires JWT)
curl -X POST https://your-api.com/api/v1/subscription/consume \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "text_to_image",
    "description": "Test model generation"
  }'
```

---

## Migration from Old System

If you were previously sending `amount` directly:

### Old Code (❌):
```javascript
await fetch('/api/v1/subscription/consume', {
  body: JSON.stringify({
    amount: 10,  // ❌ No longer works
    description: "Generated model"
  })
});
```

### New Code (✅):
```javascript
await fetch('/api/v1/subscription/consume', {
  body: JSON.stringify({
    operation: "text_to_image",  // ✅ Backend determines cost
    description: "Generated model"
  })
});
```

---

## Need Help?

- Backend determines all costs - see `app/core/token_costs.py`
- To add new operations, update backend first, then use the new operation name
- For cost changes, only backend needs updating (no frontend changes required)

---

**That's it!** The backend now controls all token costs, making it:
- ✅ More secure (frontend can't manipulate costs)
- ✅ Easier to update (change costs without deploying frontend)
- ✅ Single source of truth (all costs in one place)

