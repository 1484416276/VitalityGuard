import Foundation
import Combine
import UserNotifications

enum TimerState {
    case idle
    case working
    case countdown
    case resting
    case nightRest
}

class TimerManager: ObservableObject {
    @Published var state: TimerState = .idle
    @Published var remainingSeconds: Int = 0
    @Published var config: AppConfig
    @Published var showRestScreen: Bool = false
    
    private var timer: Timer?
    private var escPressCount: Int = 0
    private var lastEscPressTime: Date?
    
    init() {
        self.config = AppConfig.load()
    }
    
    func startWorkCycle() {
        guard config.isEnabled else { return }
        
        if config.isNightRestTime() {
            startNightRest()
            return
        }
        
        stopTimer()
        state = .working
        remainingSeconds = config.workDuration * 60
        startTimer()
    }
    
    func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }
    
    func stopTimer() {
        timer?.invalidate()
        timer = nil
    }
    
    private func tick() {
        remainingSeconds -= 1
        
        if remainingSeconds <= 0 {
            transitionToNextState()
        }
    }
    
    private func transitionToNextState() {
        switch state {
        case .working:
            state = .countdown
            remainingSeconds = config.countdownDuration
            sendNotification(title: NSLocalizedString("rest_reminder", comment: ""), body: NSLocalizedString("rest_soon", comment: ""))
            
        case .countdown:
            state = .resting
            remainingSeconds = config.restDuration * 60
            showRestScreen = true
            sendNotification(title: NSLocalizedString("rest_time", comment: ""), body: NSLocalizedString("rest_now", comment: ""))
            
        case .resting:
            showRestScreen = false
            startWorkCycle()
            
        case .nightRest:
            if !config.isNightRestTime() {
                startWorkCycle()
            } else {
                remainingSeconds = 60
            }
            
        case .idle:
            break
        }
    }
    
    func startNightRest() {
        stopTimer()
        state = .nightRest
        showRestScreen = true
        remainingSeconds = 60
        startTimer()
        sendNotification(title: NSLocalizedString("night_rest", comment: ""), body: NSLocalizedString("night_rest_message", comment: ""))
    }
    
    func emergencyUnlock() {
        guard config.allowUnlock, state == .resting else { return }
        showRestScreen = false
        startWorkCycle()
    }
    
    func handleEscPress() {
        guard config.allowUnlock, state == .resting else { return }
        
        let now = Date()
        if let lastPress = lastEscPressTime, now.timeIntervalSince(lastPress) < 1.0 {
            escPressCount += 1
            if escPressCount >= 5 {
                emergencyUnlock()
                escPressCount = 0
            }
        } else {
            escPressCount = 1
        }
        lastEscPressTime = now
    }
    
    func pauseWork() {
        stopTimer()
        state = .idle
    }
    
    func resumeWork() {
        startWorkCycle()
    }
    
    func updateConfig(_ newConfig: AppConfig) {
        config = newConfig
        config.save()
        
        if state != .idle {
            startWorkCycle()
        }
    }
    
    private func sendNotification(title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }
    
    func formattedTime() -> String {
        let hours = remainingSeconds / 3600
        let minutes = (remainingSeconds % 3600) / 60
        let seconds = remainingSeconds % 60
        
        if hours > 0 {
            return String(format: "%02d:%02d:%02d", hours, minutes, seconds)
        } else {
            return String(format: "%02d:%02d", minutes, seconds)
        }
    }
}
