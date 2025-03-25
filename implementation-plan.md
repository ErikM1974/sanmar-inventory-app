# Implementation Plan: Dynamic Product Pricing for Color Swatch Selection

## Overview
This document outlines the implementation plan for fetching and displaying product pricing when a color swatch is selected in the SanMar Inventory Application. The implementation will make AJAX requests to fetch real-time pricing data from SanMar's Pricing API.

## Requirements
- Lightweight implementation to ensure good performance
- Support for both mouse clicks and touch events for mobile users
- Implementation of both client-side and server-side caching
- Prioritization of pricing data correctness over performance
- Support for both request formats (style/color/size and inventoryKey/sizeIndex)

## Implementation Components

### 1. Backend Components

#### 1.1 New API Endpoint
- Create a Flask route `/api/pricing/<style>/<color>` that accepts AJAX requests
- The endpoint will use the existing SanMar pricing service to fetch real-time pricing data
- Return the pricing data as JSON with appropriate headers for caching

#### 1.2 Enhanced SanMar Pricing Service
- Extend the existing `SanmarPricingService` class to support both request formats:
  - style/color/size format (primary)
  - inventoryKey/sizeIndex format (fallback)
- Implement environment-aware endpoint URL selection:
  - Development: `https://edev-ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl`
  - Production: `https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl`
- Add XML parsing functionality to extract all pricing details:
  - Piece price
  - Dozen price
  - Case price
  - Sale price
  - Customer-specific pricing (my price)
  - Sale start/end dates

#### 1.3 Server-Side Caching
- Implement in-memory cache for pricing data
- Use style+color combination as cache key
- Set TTL of 15 minutes for cached data
- Implement cache invalidation for specific products when needed

### 2. Frontend Components

#### 2.1 JavaScript Updates
- Modify the `selectColor` function in product.html to:
  - Make AJAX calls to the new API endpoint
  - Support both mouse clicks and touch events
  - Handle loading states and errors gracefully
  - Display appropriate user feedback

#### 2.2 Client-Side Caching
- Implement localStorage-based caching
- Store pricing data with style+color as key
- Set expiration timestamp of 30 minutes
- Check cache before making AJAX requests

#### 2.3 UI Enhancements
- Add loading indicator while prices are being fetched
- Display error messages if pricing fetch fails
- Ensure responsive design for all device sizes
- Maintain accessibility standards

### 3. Error Handling

#### 3.1 API Error Handling
- Implement comprehensive error handling for:
  - Network failures
  - API timeouts
  - Authentication failures
  - Malformed responses
- Log detailed error information for debugging
- Return user-friendly error messages

#### 3.2 Fallback Mechanisms
- Default to style/color/size format, fallback to inventoryKey/sizeIndex
- If no pricing data is available, show default pricing
- Cache partial results when complete data isn't available

### 4. Testing Strategy

#### 4.1 Unit Tests
- Test XML parsing functionality
- Test caching mechanisms
- Test both request formats

#### 4.2 Integration Tests
- Test end-to-end flow from color selection to pricing display
- Test with various product styles and colors
- Test error scenarios and fallback mechanisms

#### 4.3 Performance Tests
- Measure response times with and without caching
- Ensure acceptable performance on mobile devices

## Implementation Sequence

1. Update SanmarPricingService with environment selection and enhanced XML parsing
2. Implement server-side caching in the pricing service
3. Create the new API endpoint in app.py
4. Update the JavaScript in product.html for AJAX requests
5. Implement client-side caching
6. Add UI enhancements and error handling
7. Test all components thoroughly

## Success Criteria
- Real-time pricing data is displayed when a color swatch is selected
- The UI remains responsive during pricing data fetching
- Caching mechanisms reduce load on the SanMar API
- Error handling provides a graceful user experience
- Implementation works across all target browsers and devices