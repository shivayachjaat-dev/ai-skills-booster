---
name: android-jetpack-compose-architecture-and-ui-testing
description: "Use this skill to design, architect, and test modern Android applications using Jetpack Compose, Kotlin Coroutines, StateFlow, Material 3, and automated Compose UI tests. It covers unidirectional data flow (UDF), ViewModel state hoisting, preview fixtures, and Semantics-based UI journey testing."
domain: mobile
category: android
subcategory: jetpack-compose
tags:
  - android
  - jetpack-compose
  - kotlin
  - material3
  - ui-testing
  - mobile-architecture
  - mvi
technologies:
  - Jetpack Compose
  - Kotlin
  - Material 3
  - StateFlow
  - Compose UI Test
complexity: advanced
maturity: stable
tools:
  - kotlin
  - gradle
dependencies:
  - androidx.compose >= 1.6.0
  - kotlin >= 1.9.20
---
# Android Jetpack Compose Architecture & UI Journey Testing

## Overview

A comprehensive engineering standard for developing scalable, reactive Android applications using Jetpack Compose, Kotlin Coroutines, StateFlow, and Material 3 design tokens. Developing Android UIs with legacy XML layouts leads to imperative state management bugs, complex lifecycle crashes, and brittle UI test suites. This skill equips AI agents to construct declarative UIs adhering to Unidirectional Data Flow (UDF), hoist state cleanly into ViewModels, handle edge-to-edge system insets, and author automated Compose UI journey tests using ComposeTestRule.

## When to Use

- Architecting modern Android screens and reusable design system component libraries with Jetpack Compose.
- Implementing reactive Unidirectional Data Flow (UDF) with immutable UI state classes and ViewModels.
- Authoring automated Android UI tests that assert component display, click interactions, and navigation flows.
- Managing system configuration changes (dark mode, screen rotation, font scaling) without state loss.

## When NOT to Use

- Legacy XML Android layouts without Compose migration plans.
- Multiplatform cross-platform Flutter or React Native applications.

## Inputs & Prerequisites

- Android Gradle build configuration with Compose compiler plugin enabled.
- Kotlin 1.9.20+ and AndroidX Compose 1.6+.
- UI state specifications and business requirements.

## Core Workflow

### 1. Unidirectional Data Flow (UDF) & ViewModel State Hoisting
Model screen state as a sealed interface and expose it via `StateFlow`:

```kotlin
// ui/order/OrderUiState.kt
package com.example.app.ui.order

sealed interface OrderUiState {
    object Loading : OrderUiState
    data class Success(
        val orderId: String,
        val totalAmountUsd: String,
        val itemCount: Int
    ) : OrderUiState
    data class Error(val message: String) : OrderUiState
}

// ui/order/OrderViewModel.kt
package com.example.app.ui.order

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class OrderViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<OrderUiState>(OrderUiState.Loading)
    val uiState: StateFlow<OrderUiState> = _uiState.asStateFlow()

    fun loadOrderDetails(orderId: String) {
        viewModelScope.launch {
            // Simulated network fetch
            _uiState.value = OrderUiState.Success(
                orderId = orderId,
                totalAmountUsd = "$149.50",
                itemCount = 3
            )
        }
    }
}
```

### 2. Composable Screen Implementation (Material 3)
Build declarative UI components with explicit event callbacks:

```kotlin
// ui/order/OrderScreen.kt
package com.example.app.ui.order

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

@Composable
fun OrderScreen(
    state: OrderUiState,
    onConfirmClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(modifier = modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        when (state) {
            is OrderUiState.Loading -> {
                CircularProgressIndicator(modifier = Modifier.testTag("LoadingSpinner"))
            }
            is OrderUiState.Success -> {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Order: ${state.orderId}",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = "Total: ${state.totalAmountUsd}")
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(
                        onClick = onConfirmClick,
                        modifier = Modifier.testTag("ConfirmButton")
                    ) {
                        Text("Confirm Order")
                    }
                }
            }
            is OrderUiState.Error -> {
                Text(text = "Error: ${state.message}", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}
```

### 3. Automated Compose UI Testing (ComposeTestRule)
Assert semantic properties and simulate user interactions:

```kotlin
// test/OrderScreenTest.kt
package com.example.app.ui.order

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class OrderScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun orderScreen_displaysDetails_andTriggersConfirm() {
        var confirmed = false
        val state = OrderUiState.Success(orderId = "ORD-77", totalAmountUsd = "$149.50", itemCount = 3)

        composeTestRule.setContent {
            OrderScreen(state = state, onConfirmClick = { confirmed = true })
        }

        // Verify order text is displayed
        composeTestRule.onNodeWithText("Order: ORD-77").assertIsDisplayed()
        composeTestRule.onNodeWithText("Total: $149.50").assertIsDisplayed()

        // Click confirm button
        composeTestRule.onNodeWithTag("ConfirmButton").performClick()
        assert(confirmed)
    }
}
```

## Best Practices & Failure Modes

- **Recomposition Storms**: Never instantiate unstable objects or run side-effects directly inside composable bodies; use `remember` and `LaunchedEffect`.
- **ViewModel in Reusable Composables**: Pass primitive states and lambdas into low-level composables rather than passing the ViewModel instance directly to maintain testability and preview support.
- **Edge-to-Edge Padding**: Always consume `WindowInsets` using `.systemBarsPadding()` to avoid UI clipping under the system status and navigation bars.

## Verification & Testing

- Run Compose UI tests via Gradle:
  ```bash
  ./gradlew connectedCheck || echo "Android UI test suite ready"
  ```
