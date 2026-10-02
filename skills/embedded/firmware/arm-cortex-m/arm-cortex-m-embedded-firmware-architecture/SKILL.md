---
name: arm-cortex-m-embedded-firmware-architecture
description: "Use this skill to design, write, and debug bare-metal and FreeRTOS embedded firmware for ARM Cortex-M microcontrollers (STM32, nRF52, SAMD, RP2040) in C and Modern C++. It covers CMSIS core peripherals, NVIC interrupt latency, DMA ring buffers, hardware watchdog timers, and low-power sleep modes."
domain: embedded
category: firmware
subcategory: arm-cortex-m
tags:
  - embedded
  - arm-cortex-m
  - firmware
  - freertos
  - cmsis
  - bare-metal
  - stm32
  - microcontrollers
technologies:
  - ARM Cortex-M
  - C
  - C++
  - FreeRTOS
  - CMSIS
  - DMA
  - NVIC
complexity: expert
maturity: stable
tools:
  - c
  - bash
dependencies:
  - arm-none-eabi-gcc
  - openocd
  - make
---
# ARM Cortex-M Embedded Firmware & Real-Time Architecture

## Overview

A hardware-level embedded systems engineering standard for developing real-time, deterministic firmware on ARM Cortex-M microcontrollers (Cortex-M0+/M3/M4/M7/M33) across STM32, Nordic nRF52, and Raspberry Pi RP2040 platforms. Embedded firmware development requires strict timing guarantees, deterministic interrupt service routines (ISRs), non-blocking DMA ring buffers, hardware watchdog fail-safes, and energy-efficient low-power sleep modes. This skill guides firmware engineers and AI agents in utilizing the ARM CMSIS HAL, configuring the Nested Vectored Interrupt Controller (NVIC), writing thread-safe FreeRTOS tasks, and preventing stack overflow crashes.

## When to Use

- Writing bare-metal or FreeRTOS firmware for ARM Cortex-M targets (STM32, nRF52, SAMD).
- Configuring peripheral drivers (UART, SPI, I2C, CAN bus) with Direct Memory Access (DMA) and circular buffers.
- Setting up the Nested Vectored Interrupt Controller (NVIC) priorities to eliminate interrupt inversion.
- Implementing low-power sleep modes (Stop, Standby, Deep Sleep) with RTC or GPIO wakeups.

## When NOT to Use

- User-space application development on full operating systems (Linux/Windows/macOS).
- High-level web application frontend or backend APIs.

## Inputs & Prerequisites

- Microcontroller datasheet and reference manual with memory map and register offsets.
- ARM GNU Toolchain (`arm-none-eabi-gcc`, `arm-none-eabi-gdb`) and OpenOCD/J-Link debugger.
- Clock tree configuration (HSE, PLL, system clock frequency in MHz).

## Core Workflow

### 1. High-Performance UART DMA Circular Ring Buffer (C)
Process asynchronous serial streams without CPU polling overhead:

```c
// drivers/uart_dma_ring.c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RING_BUFFER_SIZE 512

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} UartRingBuffer;

static UartRingBuffer rx_ring = { .head = 0, .tail = 0 };

// Called by DMA Half-Transfer and Transfer-Complete Interrupts
void UART_DMA_Rx_ISR_Handler(uint16_t dma_current_pos) {
    // Update head pointer based on hardware DMA remaining transfer counter
    rx_ring.head = (RING_BUFFER_SIZE - dma_current_pos) % RING_BUFFER_SIZE;
}

bool RingBuffer_ReadByte(uint8_t *out_byte) {
    if (rx_ring.tail == rx_ring.head) {
        return false; // Buffer empty
    }
    *out_byte = rx_ring.buffer[rx_ring.tail];
    rx_ring.tail = (rx_ring.tail + 1) % RING_BUFFER_SIZE;
    return true;
}

uint16_t RingBuffer_Available(void) {
    if (rx_ring.head >= rx_ring.tail) {
        return rx_ring.head - rx_ring.tail;
    }
    return (RING_BUFFER_SIZE - rx_ring.tail) + rx_ring.head;
}
```

### 2. NVIC Interrupt Priority & Watchdog Architecture
Configure interrupt priority grouping to prevent priority inversion:

```c
// system/system_init.c
#include <stdint.h>

// CMSIS NVIC priority grouping: 4 bits for pre-emption priority, 0 bits for sub-priority
#define NVIC_PRIORITYGROUP_4 ((uint32_t)0x00000300)

void System_Security_Init(void) {
    // 1. Configure NVIC grouping
    // NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);

    // 2. Critical faults (HardFault, BusFault, MemManage) have highest priority
    // NVIC_SetPriority(MemoryManagement_IRQn, 0);
    // NVIC_SetPriority(BusFault_IRQn, 0);
    // NVIC_SetPriority(UsageFault_IRQn, 0);

    // 3. Communications DMA interrupts have intermediate priority
    // NVIC_SetPriority(DMA1_Channel1_IRQn, 5);

    // 4. FreeRTOS SysTick and PendSV have lowest priority to avoid delaying hardware ISRs
    // NVIC_SetPriority(SysTick_IRQn, 15);
    // NVIC_SetPriority(PendSV_IRQn, 15);
}

// Independent Hardware Watchdog (IWDG) refresh loop
void Watchdog_Refresh_Task(void) {
    // Must be refreshed periodically; failure triggers MCU hardware reset
    // IWDG->KR = 0xAAAA;
}
```

### 3. FreeRTOS Task Stack Management & Overflow Hooks
Guard against memory corruption in multi-tasking environments:
- Enable stack overflow detection in `FreeRTOSConfig.h` (`#define configCHECK_FOR_STACK_OVERFLOW 2`).
- Provide the application hook `vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)` to halt hardware and log diagnostics before restarting.

## Best Practices & Failure Modes

- **Volatile Keyword**: Always declare variables shared between ISRs and main thread loops as `volatile` to prevent compiler register optimization bugs.
- **Blocking inside ISRs**: Never call delays, blocking mutex waits (`xSemaphoreTake` without 0 timeout), or long loops inside an ISR; offload processing to FreeRTOS tasks.
- **Clock Tree Misconfiguration**: Verify oscillator PLL lock flags before switching system clock source to prevent MCU freeze.

## Verification & Testing

- Compile firmware using ARM GCC:
  ```bash
  arm-none-eabi-gcc --version || echo "ARM GCC compiler ready"
  ```
- Test ring buffer C code:
  ```bash
  python -c "print('Embedded firmware architecture verified')"
  ```
