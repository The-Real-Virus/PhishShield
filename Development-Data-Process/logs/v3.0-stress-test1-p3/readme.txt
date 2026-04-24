Phase C: Performance Profiling (The "Silent" Test)
Industry buyers will reject an extension if it slows down employees' computers.

Memory Leak Check: Open Chrome DevTools -> Performance. We will record the extension's memory usage while opening 50 tabs to ensure the Offscreen Document for visual hashing isn't eating RAM.

Latency Measurement: We must prove that Layer 1 and 2 execute in under 50ms, and Layer 3 executes in under 500ms so the user never feels a delay.