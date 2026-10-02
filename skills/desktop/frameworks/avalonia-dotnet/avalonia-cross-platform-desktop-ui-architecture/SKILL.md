---
name: avalonia-cross-platform-desktop-ui-architecture
description: "Use this skill to design, build, and optimize high-performance cross-platform desktop applications using Avalonia UI and .NET 8/9. It covers MVVM architecture with ReactiveUI and CommunityToolkit.Mvvm, fluent UI themes and dark mode switching, asynchronous relay commands, virtualized data grids, custom template controls, and native packaging for Windows, macOS, and Linux."
domain: desktop
category: frameworks
subcategory: avalonia-dotnet
tags:
  - desktop
  - avalonia
  - dotnet
  - csharp
  - mvvm
  - cross-platform
  - reactiveui
  - ui-architecture
technologies:
  - Avalonia UI
  - C#
  - .NET 8
  - .NET 9
  - ReactiveUI
  - XAML
complexity: advanced
maturity: stable
tools:
  - dotnet
  - bash
dependencies:
  - Avalonia@>=11.0.0
  - CommunityToolkit.Mvvm@>=8.2.0
---
# Avalonia UI Cross-Platform Desktop Architecture

## Overview

A modern .NET engineering standard for architecting robust, native-performing cross-platform desktop applications using Avalonia UI (v11+) and .NET 8/9. Unlike platform-tied frameworks (WPF on Windows, Cocoa on macOS), Avalonia utilizes its own Skia-based rendering pipeline to provide identical visual fidelity, layout precision, and styling semantics across Windows, macOS, and Linux from a single C# codebase. This skill guides desktop engineers and AI agents in structuring scalable MVVM architectures, implementing compiled bindings, handling responsive multi-threaded async UI updates, and building fluid user interfaces.

```
+------------------------------------------------------------------------+
|                      Avalonia UI Multi-Platform Engine                 |
|                                                                        |
|  [ View (XAML / AXAML) ] <---(Compiled Bindings)---> [ ViewModel ]     |
|      (FluentTheme / Styles)                           (CommunityToolkit)|
|                                                              |         |
|                                                              v         |
|                                                      [ Model & Services|
|                                                                        |
|  Rendering Pipeline (SkiaSharp / Top-Level Native Window):             |
|  +-------------------+  +-------------------+  +--------------------+  |
|  | Windows (DirectX) |  | macOS (Metal)     |  | Linux (Vulkan/X11) |  |
|  +-------------------+  +-------------------+  +--------------------+  |
+------------------------------------------------------------------------+
```

## When to Use

- Developing enterprise desktop tools, scientific instrument GUIs, media workstations, or offline-first client apps targeting Windows, macOS, and Linux simultaneously.
- Migrating legacy WPF, Silverlight, or WinForms applications to modern cross-platform .NET.
- Building complex desktop interfaces with high-density data grids, interactive canvas layouts, and custom theme styling.

## When NOT to Use

- Pure web browser applications (use Astro, React, or Blazor WebAssembly).
- Mobile-first consumer apps prioritizing native iOS/Android system controls over unified desktop canvas rendering.

## Inputs & Prerequisites

- .NET 8.0 SDK or .NET 9.0 SDK installed.
- Avalonia templates (`dotnet new install Avalonia.Templates`).
- IDE: JetBrains Rider, Visual Studio 2022, or VS Code with C# Dev Kit.

## Core Workflow

### Step 1: Project Scaffolding and Dependency Setup
Initialize an Avalonia MVVM project using `CommunityToolkit.Mvvm`:

```bash
dotnet new avalonia.mvvm -n EnterpriseDesktopApp
cd EnterpriseDesktopApp
dotnet add package CommunityToolkit.Mvvm --version 8.2.2
```

### Step 2: Observable ViewModel with Async Relay Commands
Implement clean, boilerplate-free ViewModels using C# source generators:

```csharp
using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace EnterpriseDesktopApp.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private bool _isLoading = false;

    public ObservableCollection<string> ConnectedNodes { get; } = new();

    [RelayCommand]
    private async Task RefreshClusterStatusAsync()
    {
        IsLoading = true;
        StatusMessage = "Querying distributed nodes...";

        try
        {
            await Task.Delay(1000); // Simulate network query
            ConnectedNodes.Clear();
            ConnectedNodes.Add("Node-US-East (Latency: 12ms)");
            ConnectedNodes.Add("Node-EU-Central (Latency: 84ms)");
            StatusMessage = $"Cluster synchronized at {DateTime.Now:T}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
}
```

### Step 3: AXAML View with Compiled Bindings
Leverage compiled bindings (`x:DataType`) for zero-reflection performance and compile-time type safety:

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:vm="using:EnterpriseDesktopApp.ViewModels"
             x:Class="EnterpriseDesktopApp.Views.DashboardView"
             x:DataType="vm:DashboardViewModel">
    
    <Grid RowDefinitions="Auto, *, Auto" Margin="24">
        <!-- Header -->
        <StackPanel Grid.Row="0" Spacing="8">
            <TextBlock Text="Cluster Telemetry Dashboard" 
                       FontSize="24" 
                       FontWeight="SemiBold"/>
            <TextBlock Text="{Binding StatusMessage}" 
                       Foreground="{DynamicResource SystemAccentColor}"/>
        </StackPanel>

        <!-- Node List -->
        <ListBox Grid.Row="1" 
                 Margin="0,16"
                 ItemsSource="{Binding ConnectedNodes}">
            <ListBox.ItemTemplate>
                <DataTemplate>
                    <TextBlock Text="{Binding}" Padding="8,4"/>
                </DataTemplate>
            </ListBox.ItemTemplate>
        </ListBox>

        <!-- Actions -->
        <Button Grid.Row="2"
                Content="Refresh Nodes"
                Command="{Binding RefreshClusterStatusCommand}"
                IsEnabled="{Binding !IsLoading}"
                HorizontalAlignment="Right"/>
    </Grid>
</UserControl>
```

### Step 4: Fluent Theme and Dark/Light Mode Switching
Configure adaptive system theme detection in `App.axaml`:

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="EnterpriseDesktopApp.App"
             RequestedThemeVariant="Default">
    <Application.Styles>
        <FluentTheme />
    </Application.Styles>
</Application>
```

## Best Practices & Failure Modes

- **Always Use Compiled Bindings**: Set `x:CompileBindings="True"` on views. Uncompiled reflection bindings degrade rendering frame rates and mask binding typos.
- **Dispatcher UI Thread Safety**: When background events complete, ensure UI properties are only mutated on the UI thread or use `Dispatcher.UIThread.Post(...)`.
- **macOS Window Architecture**: macOS applications require proper `Info.plist` bundle identifiers, Retina display scaling support, and notarization with Apple Developer certificates.

## Verification & Testing

1. Run unit tests on ViewModels independently of the UI: `dotnet test`.
2. Compile and launch on host OS: `dotnet run`.
3. Verify cross-platform builds: Test Linux rendering using X11 / Wayland or Docker headless display.
