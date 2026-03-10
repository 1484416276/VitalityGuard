import SwiftUI

struct SettingsView: View {
    @ObservedObject var timerManager: TimerManager
    @Environment(\.dismiss) var dismiss
    @Environment(\.scenePhase) var scenePhase
    
    @State private var workDuration: Int
    @State private var restDuration: Int
    @State private var countdownDuration: Int
    @State private var nightRestEnabled: Bool
    @State private var nightRestStartHour: Int
    @State private var nightRestStartMinute: Int
    @State private var nightRestEndHour: Int
    @State private var nightRestEndMinute: Int
    @State private var allowUnlock: Bool
    @State private var isEnabled: Bool
    @State private var requireHealthTask: Bool
    @State private var strictMode: Bool
    @State private var guidedAccessReminder: Bool
    
    init(timerManager: TimerManager) {
        self.timerManager = timerManager
        _workDuration = State(initialValue: timerManager.config.workDuration)
        _restDuration = State(initialValue: timerManager.config.restDuration)
        _countdownDuration = State(initialValue: timerManager.config.countdownDuration)
        _nightRestEnabled = State(initialValue: timerManager.config.nightRestEnabled)
        _nightRestStartHour = State(initialValue: timerManager.config.nightRestStartHour)
        _nightRestStartMinute = State(initialValue: timerManager.config.nightRestStartMinute)
        _nightRestEndHour = State(initialValue: timerManager.config.nightRestEndHour)
        _nightRestEndMinute = State(initialValue: timerManager.config.nightRestEndMinute)
        _allowUnlock = State(initialValue: timerManager.config.allowUnlock)
        _isEnabled = State(initialValue: timerManager.config.isEnabled)
        _requireHealthTask = State(initialValue: timerManager.config.requireHealthTask)
        _strictMode = State(initialValue: timerManager.config.strictMode)
        _guidedAccessReminder = State(initialValue: timerManager.config.guidedAccessReminder)
    }
    
    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text(NSLocalizedString("work_rest_cycle", comment: ""))) {
                    HStack {
                        Text(NSLocalizedString("work_duration", comment: ""))
                        Spacer()
                        TextField("", value: $workDuration, formatter: NumberFormatter())
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text(NSLocalizedString("minutes", comment: ""))
                    }
                    
                    HStack {
                        Text(NSLocalizedString("rest_duration", comment: ""))
                        Spacer()
                        TextField("", value: $restDuration, formatter: NumberFormatter())
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text(NSLocalizedString("minutes", comment: ""))
                    }
                    
                    HStack {
                        Text(NSLocalizedString("countdown_duration", comment: ""))
                        Spacer()
                        TextField("", value: $countdownDuration, formatter: NumberFormatter())
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text(NSLocalizedString("seconds", comment: ""))
                    }
                }
                
                Section(header: Text(NSLocalizedString("night_rest_mode", comment: ""))) {
                    Toggle(NSLocalizedString("enable_night_rest", comment: ""), isOn: $nightRestEnabled)
                    
                    if nightRestEnabled {
                        HStack {
                            Text(NSLocalizedString("rest_period", comment: ""))
                            Spacer()
                            TextField("", value: $nightRestStartHour, formatter: NumberFormatter())
                                .keyboardType(.numberPad)
                                .frame(width: 40)
                            Text(":")
                            TextField("", value: $nightRestStartMinute, formatter: NumberFormatter())
                                .keyboardType(.numberPad)
                                .frame(width: 40)
                            Text(" - ")
                            TextField("", value: $nightRestEndHour, formatter: NumberFormatter())
                                .keyboardType(.numberPad)
                                .frame(width: 40)
                            Text(":")
                            TextField("", value: $nightRestEndMinute, formatter: NumberFormatter())
                                .keyboardType(.numberPad)
                                .frame(width: 40)
                        }
                    }
                }
                
                Section(header: Text(NSLocalizedString("enforcement_settings", comment: ""))) {
                    Toggle(NSLocalizedString("require_health_task", comment: ""), isOn: $requireHealthTask)
                    
                    if requireHealthTask {
                        Text(NSLocalizedString("health_task_hint", comment: ""))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Toggle(NSLocalizedString("guided_access_reminder", comment: ""), isOn: $guidedAccessReminder)
                    
                    if guidedAccessReminder {
                        Text(NSLocalizedString("guided_access_detail", comment: ""))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Section(header: Text(NSLocalizedString("safety_features", comment: ""))) {
                    Toggle(NSLocalizedString("allow_unlock", comment: ""), isOn: $allowUnlock)
                    if allowUnlock {
                        Text(NSLocalizedString("unlock_hint", comment: ""))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Section(header: Text(NSLocalizedString("general", comment: ""))) {
                    Toggle(NSLocalizedString("enable_assistant", comment: ""), isOn: $isEnabled)
                }
            }
            .navigationTitle(NSLocalizedString("settings", comment: ""))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(NSLocalizedString("save", comment: "")) {
                        saveConfig()
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button(NSLocalizedString("cancel", comment: "")) {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func saveConfig() {
        let newConfig = AppConfig(
            workDuration: workDuration,
            restDuration: restDuration,
            countdownDuration: countdownDuration,
            nightRestEnabled: nightRestEnabled,
            nightRestStartHour: nightRestStartHour,
            nightRestStartMinute: nightRestStartMinute,
            nightRestEndHour: nightRestEndHour,
            nightRestEndMinute: nightRestEndMinute,
            allowUnlock: allowUnlock,
            isEnabled: isEnabled,
            language: timerManager.config.language,
            requireHealthTask: requireHealthTask,
            strictMode: strictMode,
            guidedAccessReminder: guidedAccessReminder
        )
        timerManager.updateConfig(newConfig)
        dismiss()
    }
}

#Preview {
    SettingsView(timerManager: TimerManager())
}
