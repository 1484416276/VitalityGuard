import SwiftUI

@main
struct VitalityGuardApp: App {
    @StateObject private var timerManager = TimerManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(timerManager)
        }
    }
}
