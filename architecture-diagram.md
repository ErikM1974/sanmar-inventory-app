# Architecture Diagram: Dynamic Product Pricing

The following diagram illustrates the flow of data and interactions between components for the dynamic product pricing feature when a color swatch is selected.

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant LocalStorage as Browser LocalStorage
    participant Flask as Flask App
    participant MemCache as Server Memory Cache
    participant PricingService as SanMar Pricing Service
    participant SanmarAPI as SanMar SOAP API

    User->>Browser: Select color swatch
    
    Browser->>LocalStorage: Check for cached pricing
    
    alt Cache hit
        LocalStorage-->>Browser: Return cached pricing data
        Browser->>Browser: Update pricing display
    else Cache miss
        Browser->>Flask: Request /api/pricing/{style}/{color}
        
        Flask->>MemCache: Check for cached pricing
        
        alt Server cache hit
            MemCache-->>Flask: Return cached pricing data
        else Server cache miss
            Flask->>PricingService: Request pricing (style/color/size)
            
            alt Primary method succeeds
                PricingService->>SanmarAPI: Send SOAP request (style/color/size)
                SanmarAPI-->>PricingService: Return XML response
                PricingService->>PricingService: Parse XML response
            else Primary method fails
                PricingService->>SanmarAPI: Send SOAP request (inventoryKey/sizeIndex)
                SanmarAPI-->>PricingService: Return XML response
                PricingService->>PricingService: Parse XML response
            end
            
            PricingService-->>Flask: Return pricing data
            Flask->>MemCache: Store in server cache (15-min TTL)
        end
        
        Flask-->>Browser: Return JSON pricing data
        Browser->>LocalStorage: Store in client cache (30-min TTL)
        Browser->>Browser: Update pricing display
    end
    
    Browser-->>User: Display updated pricing
```

## Component Responsibilities

### Frontend Components
- **Browser**: Handles user interactions and displays pricing data
- **LocalStorage**: Provides client-side caching for 30 minutes

### Backend Components
- **Flask App**: Exposes API endpoints and coordinates pricing requests
- **Server Memory Cache**: Provides server-side caching for 15 minutes
- **SanMar Pricing Service**: Handles SOAP requests and response parsing

### External Systems
- **SanMar SOAP API**: Provides pricing data for products

## Data Flow

1. User selects a color swatch
2. Browser checks LocalStorage for cached pricing data
3. If cached data exists and is valid, display it
4. Otherwise, make AJAX request to Flask API
5. Flask checks server-side cache for pricing data
6. If server cache hit, return cached data
7. Otherwise, request pricing from SanMar Pricing Service
8. Pricing Service makes SOAP request to SanMar API
9. Parse response and return pricing data to Flask
10. Flask stores pricing in server cache and returns to browser
11. Browser stores pricing in LocalStorage and updates display

## Error Handling

- If primary request method fails, fall back to alternate method
- If all API requests fail, use default pricing data
- Client and server caching reduces impact of API failures