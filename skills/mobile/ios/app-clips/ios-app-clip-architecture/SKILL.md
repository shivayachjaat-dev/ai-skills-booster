---
name: ios-app-clip-architecture
description: "Use this skill when designing, building, and configuring iOS App Clips for on-demand, lightweight app experiences without full App Store installations. It guides the agent through Apple App Clip target creation in Xcode/Expo, bundle size optimization (< 15MB or 50MB on iOS 17+), Associated Domains configuration (appclips:), Apple Pay and Sign in with Apple integration, and App Clip code invocation."
domain: mobile
category: ios
subcategory: app-clips
tags:
  - ios
  - app-clips
  - apple
  - mobile
  - swift
  - expo
  - react-native
technologies:
  - iOS SDK
  - Swift
  - SwiftUI
  - Expo
  - React Native
  - Xcode
complexity: advanced
maturity: stable
tools:
  - xcodebuild
  - fastlane
dependencies:
  - ios >= 16.0
---
# iOS App Clip Architecture & On-Demand Execution

## Overview

A definitive mobile engineering reference for building high-conversion, lightweight iOS App Clips. App Clips provide immediate, frictionless access to specific app functionalities (e.g. paying for parking, ordering takeout, renting a scooter) via NFC tags, QR codes, Safari Smart App Banners, or Messages, without requiring users to download the full app from the App Store. This skill instructs AI agents on configuring App Clip targets in Xcode/Expo, adhering to strict binary size limits (15 MB / 50 MB on iOS 17+), configuring Associated Domains, and seamlessly transitioning users to the full application.

## When to Use

- Enabling frictionless physical-world interactions (tap NFC tag to pay or order).
- Providing instant demo experiences directly from Safari web links or QR codes.
- Streamlining checkout workflows using native Apple Pay and Sign in with Apple.
- Increasing full app conversion rates by allowing users to complete a task before downloading.

## When NOT to Use

- Apps requiring background audio playback, continuous background location tracking, or Bluetooth peripherals (App Clips are restricted from background processing).
- Heavy applications requiring large local databases (> 50 MB) or complex multi-tab navigation.

## Inputs & Prerequisites

- Apple Developer Program account with explicit App Clip App ID capabilities.
- Xcode 15+ or Expo SDK 50+ project.
- Web domain serving Apple App Site Association (AASA) file over HTTPS.

## Core Workflow

### 1. Associated Domains Configuration (`apple-app-site-association`)
Host the AASA file at `https://example.com/.well-known/apple-app-site-association` with MIME type `application/json`:

```json
{
  "appclips": {
    "apps": ["TEAM_ID.com.example.app.Clip"]
  },
  "applinks": {
    "details": [
      {
        "appIDs": ["TEAM_ID.com.example.app"],
        "components": [
          { "/": "/orders/*" }
        ]
      }
    ]
  }
}
```

### 2. SwiftUI App Clip Entry Point & URL Invocation Handling
Handle incoming invocation URLs with zero splash screen delays:

```swift
// AppClipApp.swift
import SwiftUI

@main
struct RestaurantAppClip: App {
    @StateObject private var cartManager = CartManager()

    var body: some Scene {
        WindowGroup {
            OrderView()
                .environmentObject(cartManager)
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { userActivity in
                    guard let incomingURL = userActivity.webpageURL else { return }
                    handleInvocation(url: incomingURL)
                }
        }
    }

    private func handleInvocation(url: URL) {
        // Parse payload: https://example.com/menu?table=14&restaurant_id=rest_88
        let components = URLComponents(url: url, resolvingAgainstBaseURL: true)
        let tableNumber = components?.queryItems?.first(where: { $0.name == "table" })?.value
        let restaurantId = components?.queryItems?.first(where: { $0.name == "restaurant_id" })?.value
        
        print("Invoked App Clip for restaurant: \(restaurantId ?? "none") at table: \(tableNumber ?? "0")")
    }
}
```

### 3. Native Apple Pay Integration (Frictionless Payment)
Avoid requiring users to create accounts or enter credit card numbers manually:

```swift
import PassKit

func makePaymentRequest(amount: Decimal) -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = "merchant.com.example.appclip"
    request.supportedNetworks = [.visa, .masterCard, .amex]
    request.merchantCapabilities = .threeDSecure
    request.countryCode = "US"
    request.currencyCode = "USD"
    
    request.paymentSummaryItems = [
        PKPaymentSummaryItem(label: "Table Order", amount: NSDecimalNumber(decimal: amount))
    ]
    return request
}
```

## Best Practices & Failure Modes

1. **Exceeding Strict Binary Size Limits**: On iOS 16 and earlier, the uncompressed App Clip binary cannot exceed 15 MB (50 MB on iOS 17+). If the thin binary exceeds this limit, Apple App Store Connect rejects deployment immediately. Remove unnecessary heavy third-party analytics libraries and compress image assets.
2. **Demanding Account Creation Upfront**: Forcing users to enter an email and password before taking action destroys App Clip conversion. Use Sign in with Apple and Apple Pay to complete transactions with zero typing.
3. **Missing AASA File Validation**: If the `apple-app-site-association` file returns an HTTP 301/302 redirect or lacks the `appclips` dictionary, iOS will fail to open the App Clip and fall back to opening the webpage in Safari.

## Verification & Testing

- Test local App Clip invocation in Xcode scheme:
  - Edit Scheme -> Run -> Arguments -> Environment Variables:
  - Add `_XCAppClipURL` with value `https://example.com/menu?table=14`
- Validate AASA file configuration using Apple CDN Validator:
  ```bash
  curl -v https://app-site-association.cdn-apple.com/a/v1/example.com
  ```
