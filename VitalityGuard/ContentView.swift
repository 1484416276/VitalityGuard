import SwiftUI

struct ContentView: View {
    @StateObject private var timerManager = TimerManager()
    @State private var showSettings = false
    
    var body: some View {
        ZStack {
            if timerManager.showRestScreen {
                RestScreenView(timerManager: timerManager)
            } else {
                mainView
            }
        }
        .onAppear {
            requestNotificationPermission()
            if timerManager.config.isEnabled {
                timerManager.startWorkCycle()
            }
        }
    }
    
    private var mainView: some View {
        NavigationStack {
            VStack(spacing: 40) {
                statusIcon
                statusText
                timerDisplay
                controlButtons
                Spacer()
            }
            .padding()
            .navigationTitle("VitalityGuard")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: { showSettings = true }) {
                        Image(systemName: "gearshape.fill")
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView(timerManager: timerManager)
            }
        }
    }
    
    private var statusIcon: some View {
        Group {
            switch timerManager.state {
            case .working:
                Image(systemName: "desktopcomputer")
                    .font(.system(size: 100))
                    .foregroundColor(.blue)
            case .countdown:
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 100))
                    .foregroundColor(.orange)
            case .resting:
                Image(systemName: "bed.double.fill")
                    .font(.system(size: 100))
                    .foregroundColor(.green)
            case .nightRest:
                Image(systemName: "moon.zzz.fill")
                    .font(.system(size: 100))
                    .foregroundColor(.purple)
            case .idle:
                Image(systemName: "pause.circle.fill")
                    .font(.system(size: 100))
                    .foregroundColor(.gray)
            }
        }
    }
    
    private var statusText: some View {
        Group {
            switch timerManager.state {
            case .working:
                Text(NSLocalizedString("working", comment: ""))
                    .font(.title)
                    .foregroundColor(.secondary)
            case .countdown:
                Text(NSLocalizedString("rest_soon_title", comment: ""))
                    .font(.title)
                    .foregroundColor(.orange)
            case .resting:
                Text(NSLocalizedString("resting", comment: ""))
                    .font(.title)
                    .foregroundColor(.green)
            case .nightRest:
                Text(NSLocalizedString("night_rest_time", comment: ""))
                    .font(.title)
                    .foregroundColor(.purple)
            case .idle:
                Text(NSLocalizedString("paused", comment: ""))
                    .font(.title)
                    .foregroundColor(.gray)
            }
        }
    }
    
    private var timerDisplay: some View {
        Text(timerManager.formattedTime())
            .font(.system(size: 80, weight: .bold, design: .monospaced))
            .foregroundColor(.primary)
    }
    
    private var controlButtons: some View {
        HStack(spacing: 30) {
            if timerManager.state == .idle {
                Button(action: {
                    timerManager.startWorkCycle()
                }) {
                    Label(NSLocalizedString("start", comment: ""), systemImage: "play.fill")
                        .font(.title2)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(15)
                }
            } else {
                Button(action: {
                    timerManager.pauseWork()
                }) {
                    Label(NSLocalizedString("pause", comment: ""), systemImage: "pause.fill")
                        .font(.title2)
                        .padding()
                        .background(Color.orange)
                        .foregroundColor(.white)
                        .cornerRadius(15)
                }
                
                Button(action: {
                    timerManager.startWorkCycle()
                }) {
                    Label(NSLocalizedString("reset", comment: ""), systemImage: "arrow.counterclockwise")
                        .font(.title2)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(15)
                }
            }
        }
    }
    
    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }
}

#Preview {
    ContentView()
}
