# Avalonia UI Best Practices Reference

## Core Differences from WPF
- **Cross-Platform**: Uses SkiaSharp directly; runs natively on Linux (X11/Wayland), macOS (Metal/Cocoa), and Windows (DirectX/Win32).
- **Styling System**: CSS-inspired selector syntax (`Button:pointerover`, `Button.primary`) rather than rigid WPF Triggers.
- **TopLevel & Windowing**: Supports both desktop windowing (`Window`) and single-view mobile/embedded hosts (`SingleViewApplicationLifetime`).

## Command Binding Patterns
Use `CommunityToolkit.Mvvm`:
```csharp
[RelayCommand(CanExecute = nameof(CanSubmit))]
private async Task SubmitAsync() { ... }
```
