import Foundation

struct AppConfig: Codable {
    var workDuration: Int
    var restDuration: Int
    var countdownDuration: Int
    var nightRestEnabled: Bool
    var nightRestStartHour: Int
    var nightRestStartMinute: Int
    var nightRestEndHour: Int
    var nightRestEndMinute: Int
    var allowUnlock: Bool
    var isEnabled: Bool
    var language: String
    var requireHealthTask: Bool
    var strictMode: Bool
    var guidedAccessReminder: Bool
    
    static let `default` = AppConfig(
        workDuration: 60,
        restDuration: 5,
        countdownDuration: 10,
        nightRestEnabled: false,
        nightRestStartHour: 22,
        nightRestStartMinute: 30,
        nightRestEndHour: 7,
        nightRestEndMinute: 0,
        allowUnlock: false,
        isEnabled: true,
        language: "zh-Hans",
        requireHealthTask: true,
        strictMode: true,
        guidedAccessReminder: true
    )
    
    static func load() -> AppConfig {
        guard let data = UserDefaults.standard.data(forKey: "VitalityGuardConfig"),
              let config = try? JSONDecoder().decode(AppConfig.self, from: data) else {
            return .default
        }
        return config
    }
    
    func save() {
        guard let data = try? JSONEncoder().encode(self) else { return }
        UserDefaults.standard.set(data, forKey: "VitalityGuardConfig")
    }
    
    func isNightRestTime() -> Bool {
        guard nightRestEnabled else { return false }
        
        let calendar = Calendar.current
        let now = Date()
        let components = calendar.dateComponents([.hour, .minute], from: now)
        guard let currentHour = components.hour, let currentMinute = components.minute else { return false }
        
        let currentTotalMinutes = currentHour * 60 + currentMinute
        let startTotalMinutes = nightRestStartHour * 60 + nightRestStartMinute
        let endTotalMinutes = nightRestEndHour * 60 + nightRestEndMinute
        
        if startTotalMinutes > endTotalMinutes {
            return currentTotalMinutes >= startTotalMinutes || currentTotalMinutes < endTotalMinutes
        } else {
            return currentTotalMinutes >= startTotalMinutes && currentTotalMinutes < endTotalMinutes
        }
    }
}
