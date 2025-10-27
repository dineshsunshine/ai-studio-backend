# Subscription & Token Management API Documentation

## Overview

AI Studio now has a subscription-based token system. Users are allocated tokens based on their subscription tier, and tokens are consumed when performing AI operations.

---

## Subscription Tiers

| Tier | Tokens/Month | Description |
|------|--------------|-------------|
| **Free** | 100 | Entry-level access |
| **Basic** | 300 | For light users |
| **Pro** | 1,000 | For regular users |
| **Pro+** | 3,000 | For power users |
| **Ultimate** | Unlimited | No token limits |

---

## User API Endpoints

### 1. Get Subscription Info

**Get current user's subscription and token balance.**

```
GET /api/v1/subscription/info
```

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "tier": "pro",
  "totalTokens": 1000,
  "availableTokens": 750,
  "consumedTokens": 250,
  "lifetimeConsumed": 15000,
  "isUnlimited": false,
  "periodStart": "2025-10-01T00:00:00Z",
  "periodEnd": "2025-10-31T23:59:59Z"
}
```

**Usage:**
```javascript
// Fetch subscription info on app load or dashboard page
const response = await fetch('/api/v1/subscription/info', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const subscription = await response.json();

// Display in UI
console.log(`You have ${subscription.availableTokens} tokens remaining`);
```

---

### 2. Consume Tokens

**Consume tokens when user performs an AI operation.**

```
POST /api/v1/subscription/consume
```

**Headers:**
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 10,
  "description": "Generated model image using AI"
}
```

**Response (Success):**
```json
{
  "success": true,
  "availableTokens": 740,
  "consumedTokens": 260,
  "message": "Successfully consumed 10 tokens."
}
```

**Response (Insufficient Tokens):**
```json
{
  "success": false,
  "availableTokens": 5,
  "consumedTokens": 995,
  "message": "Insufficient tokens. You need 10 but have 5."
}
```

**Usage:**
```javascript
// BEFORE performing AI operation, consume tokens
async function generateModelWithAI(promptDetails) {
  // 1. Consume tokens first
  const consumeResponse = await fetch('/api/v1/subscription/consume', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      amount: 10,  // Cost of AI generation
      description: 'AI model generation'
    })
  });
  
  const consumeResult = await consumeResponse.json();
  
  // 2. Check if successful
  if (!consumeResult.success) {
    // Show error to user
    alert(consumeResult.message);
    // Maybe show upgrade prompt
    showUpgradeModal();
    return;
  }
  
  // 3. Proceed with AI generation
  const modelResponse = await fetch('/api/v1/models/', {
    method: 'POST',
    // ... your model creation logic
  });
  
  // 4. Update token display in UI
  updateTokenDisplay(consumeResult.availableTokens);
}
```

---

### 3. Get Token History

**View transaction history (consumption, top-ups, tier changes).**

```
GET /api/v1/subscription/history?skip=0&limit=20
```

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "transactions": [
    {
      "id": "txn-uuid",
      "type": "consumption",
      "amount": -10,
      "description": "Generated model image",
      "balanceBefore": 750,
      "balanceAfter": 740,
      "createdAt": "2025-10-17T10:30:00Z",
      "adminEmail": null
    },
    {
      "id": "txn-uuid-2",
      "type": "topup",
      "amount": 100,
      "description": "Admin top-up",
      "balanceBefore": 650,
      "balanceAfter": 750,
      "createdAt": "2025-10-15T14:20:00Z",
      "adminEmail": "admin@example.com"
    }
  ],
  "total": 45
}
```

**Usage:**
```javascript
// Show in a history/transactions page
const response = await fetch('/api/v1/subscription/history?skip=0&limit=20', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const history = await response.json();

// Display in table/list
history.transactions.forEach(txn => {
  console.log(`${txn.type}: ${txn.amount} tokens - ${txn.description}`);
});
```

---

### 4. Get Available Tiers

**Get information about all subscription tiers.**

```
GET /api/v1/subscription/tiers
```

**Response:**
```json
{
  "tiers": [
    {
      "tier": "free",
      "name": "Free",
      "tokensPerMonth": 100,
      "isUnlimited": false
    },
    {
      "tier": "basic",
      "name": "Basic",
      "tokensPerMonth": 300,
      "isUnlimited": false
    },
    {
      "tier": "pro",
      "name": "Pro",
      "tokensPerMonth": 1000,
      "isUnlimited": false
    },
    {
      "tier": "pro_plus",
      "name": "Pro+",
      "tokensPerMonth": 3000,
      "isUnlimited": false
    },
    {
      "tier": "ultimate",
      "name": "Ultimate",
      "tokensPerMonth": 0,
      "isUnlimited": true
    }
  ]
}
```

**Usage:**
```javascript
// Show in pricing/upgrade page
const response = await fetch('/api/v1/subscription/tiers');
const { tiers } = await response.json();

// Display tier options
tiers.forEach(tier => {
  console.log(`${tier.name}: ${tier.isUnlimited ? 'Unlimited' : tier.tokensPerMonth} tokens/month`);
});
```

---

## Admin API Endpoints

### 1. Get User's Subscription (Admin)

**View any user's subscription details.**

```
GET /api/v1/admin/users/{user_id}/subscription
```

**Headers:**
```
Authorization: Bearer {admin_jwt_token}
```

**Response:**
```json
{
  "userId": "user-uuid",
  "userEmail": "user@example.com",
  "tier": "pro",
  "totalTokens": 1000,
  "availableTokens": 750,
  "consumedTokens": 250,
  "lifetimeConsumed": 15000,
  "isUnlimited": false,
  "periodStart": "2025-10-01T00:00:00Z",
  "periodEnd": "2025-10-31T23:59:59Z",
  "lastTransaction": {
    "id": "txn-uuid",
    "type": "consumption",
    "amount": -10,
    "description": "Generated model image",
    "balanceBefore": 760,
    "balanceAfter": 750,
    "createdAt": "2025-10-17T10:30:00Z",
    "adminEmail": null
  }
}
```

---

### 2. Update User's Tier (Admin)

**Change a user's subscription tier.**

```
PUT /api/v1/admin/users/{user_id}/subscription/tier
```

**Headers:**
```
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "tier": "pro_plus"
}
```

**Valid tier values:**
- `"free"`
- `"basic"`
- `"pro"`
- `"pro_plus"`
- `"ultimate"`

**Response:**
```json
{
  "status": "success",
  "message": "User tier updated to pro_plus",
  "subscription": {
    "tier": "pro_plus",
    "totalTokens": 3000,
    "availableTokens": 3000,
    "isUnlimited": false
  }
}
```

**Usage:**
```javascript
// Admin updates user tier
async function updateUserTier(userId, newTier) {
  const response = await fetch(`/api/v1/admin/users/${userId}/subscription/tier`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      tier: newTier  // e.g., "pro_plus"
    })
  });
  
  const result = await response.json();
  alert(result.message);
}
```

---

### 3. Top-Up User Tokens (Admin)

**Add bonus tokens to a user's account.**

```
POST /api/v1/admin/users/{user_id}/subscription/topup
```

**Headers:**
```
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 500,
  "description": "Bonus tokens for promotional campaign"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Added 500 tokens to user's account",
  "subscription": {
    "availableTokens": 1250,
    "totalTokens": 1500
  }
}
```

**Usage:**
```javascript
// Admin gives user bonus tokens
async function topUpUserTokens(userId, amount, reason) {
  const response = await fetch(`/api/v1/admin/users/${userId}/subscription/topup`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      amount: amount,
      description: reason
    })
  });
  
  const result = await response.json();
  console.log(result.message);
}
```

---

### 4. Reset Billing Period (Admin)

**Manually reset a user's billing period.**

```
POST /api/v1/admin/users/{user_id}/subscription/reset-period
```

**Headers:**
```
Authorization: Bearer {admin_jwt_token}
```

**Response:**
```json
{
  "status": "success",
  "message": "Billing period reset successfully",
  "subscription": {
    "periodStart": "2025-10-17T00:00:00Z",
    "periodEnd": "2025-11-17T00:00:00Z",
    "availableTokens": 1000,
    "consumedTokens": 0
  }
}
```

---

## Token Costs Reference

**Suggested token costs for different operations:**

| Operation | Tokens | Description |
|-----------|--------|-------------|
| AI Model Generation | 10 | Generate a model image with AI |
| AI Look Generation | 15 | Generate a complete look |
| AI Copywriting | 5 | Generate product descriptions |
| Image Upload/Processing | 1 | Upload and process an image |
| Finishing Studio Edit | 8 | Apply AI finishing effects |

**Note:** These are suggestions. You can adjust costs based on computational requirements.

---

## Implementation Checklist

### For Regular Features:

- [ ] Display user's token balance prominently in header/dashboard
- [ ] Before any AI operation, call `/subscription/consume` endpoint
- [ ] Handle insufficient tokens gracefully (show upgrade prompt)
- [ ] Update token balance in UI after consumption
- [ ] Show token costs before user confirms operation
- [ ] Add a "Token History" page to show transaction history

### For Admin Panel:

- [ ] Add "Subscription" tab in user management
- [ ] Show current tier and token balance for each user
- [ ] Add dropdown to change user's tier
- [ ] Add input to top-up user's tokens
- [ ] Add button to reset billing period
- [ ] Show token transaction history for user

### UI/UX Recommendations:

1. **Token Display:**
   ```
   🪙 750 / 1,000 tokens remaining
   ```

2. **Low Balance Warning:**
   ```
   ⚠️  Only 50 tokens left! Upgrade to continue.
   ```

3. **Before AI Operation:**
   ```
   This will use 10 tokens. Continue?
   [Cancel] [Generate (10 🪙)]
   ```

4. **Insufficient Tokens:**
   ```
   ❌ Not enough tokens!
   You need 10 tokens but have 5.
   [Upgrade Plan] [View History]
   ```

---

## Testing URLs

**Development:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/subscription/...
```

**Production:**
```
https://ai-studio-backend-ijkp.onrender.com/api/v1/subscription/...
```

**Swagger Documentation:**
- Dev: https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/docs
- Prod: https://ai-studio-backend-ijkp.onrender.com/api/v1/docs

Look for "subscription" and "admin-subscription" tags in Swagger.

---

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK** - Success
- **400 Bad Request** - Invalid input (e.g., invalid tier name)
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Not authorized (e.g., non-admin accessing admin endpoint)
- **404 Not Found** - User or subscription not found

Example error response:
```json
{
  "detail": "User not found"
}
```

---

## Questions?

Contact the backend team or check the Swagger documentation for more details!

