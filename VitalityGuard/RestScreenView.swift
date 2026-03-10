import SwiftUI

enum HealthTask: Int, CaseIterable {
    case eyeExercise1
    case eyeExercise2
    case eyeExercise3
    case stretch
    case deepBreath
    
    var title: String {
        switch self {
        case .eyeExercise1: return NSLocalizedString("eye_exercise_1", comment: "")
        case .eyeExercise2: return NSLocalizedString("eye_exercise_2", comment: "")
        case .eyeExercise3: return NSLocalizedString("eye_exercise_3", comment: "")
        case .stretch: return NSLocalizedString("stretch", comment: "")
        case .deepBreath: return NSLocalizedString("deep_breath", comment: "")
        }
    }
    
    var instruction: String {
        switch self {
        case .eyeExercise1: return NSLocalizedString("eye_exercise_1_instruction", comment: "")
        case .eyeExercise2: return NSLocalizedString("eye_exercise_2_instruction", comment: "")
        case .eyeExercise3: return NSLocalizedString("eye_exercise_3_instruction", comment: "")
        case .stretch: return NSLocalizedString("stretch_instruction", comment: "")
        case .deepBreath: return NSLocalizedString("deep_breath_instruction", comment: "")
        }
    }
    
    var duration: Int {
        switch self {
        case .eyeExercise1, .eyeExercise2, .eyeExercise3: return 30
        case .stretch: return 20
        case .deepBreath: return 15
        }
    }
    
    var icon: String {
        switch self {
        case .eyeExercise1, .eyeExercise2, .eyeExercise3: return "eye.fill"
        case .stretch: return "figure.walk"
        case .deepBreath: return "wind"
        }
    }
    
    static func randomTasks(count: Int) -> [HealthTask] {
        let shuffled = allCases.shuffled()
        return Array(shuffled.prefix(min(count, shuffled.count)))
    }
}

struct RestScreenView: View {
    @ObservedObject var timerManager: TimerManager
    @State private var currentTaskIndex = 0
    @State private var taskProgress: CGFloat = 0
    @State private var taskTimer: Timer?
    @State private var showGuidedAccessHint = true
    @State private var tasks: [HealthTask] = []
    @State private var completedTasks: Set<Int> = []
    @State private var showCompletionAnimation = false
    @Environment(\.scenePhase) var scenePhase
    
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            if timerManager.state == .nightRest {
                nightRestView
            } else {
                restView
            }
        }
        .statusBar(hidden: true)
        .persistentSystemOverlays(.hidden)
        .onAppear {
            setupRestScreen()
            UIApplication.shared.isIdleTimerDisabled = true
        }
        .onDisappear {
            cleanupRestScreen()
            UIApplication.shared.isIdleTimerDisabled = false
        }
        .onChange(of: scenePhase) { newPhase in
            if newPhase == .active && timerManager.showRestScreen {
                UIApplication.shared.isIdleTimerDisabled = true
            }
        }
    }
    
    private var nightRestView: some View {
        VStack(spacing: 40) {
            Image(systemName: "moon.zzz.fill")
                .font(.system(size: 100))
                .foregroundColor(.blue)
                .symbolEffect(.pulse)
            
            Text(NSLocalizedString("night_rest_time", comment: ""))
                .font(.system(size: 36, weight: .bold))
                .foregroundColor(.white)
            
            Text(NSLocalizedString("please_rest_early", comment: ""))
                .font(.title2)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
            
            if timerManager.config.guidedAccessReminder {
                guidedAccessHint
                    .padding(.top, 40)
            }
        }
    }
    
    private var restView: some View {
        VStack(spacing: 30) {
            if timerManager.config.requireHealthTask && !tasks.isEmpty && currentTaskIndex < tasks.count {
                healthTaskView
            } else {
                basicRestView
            }
            
            if timerManager.config.guidedAccessReminder && showGuidedAccessHint {
                guidedAccessHint
            }
        }
        .padding()
    }
    
    private var healthTaskView: some View {
        VStack(spacing: 30) {
            Text(NSLocalizedString("complete_health_task", comment: ""))
                .font(.title2)
                .foregroundColor(.orange)
            
            let currentTask = tasks[currentTaskIndex]
            
            Image(systemName: currentTask.icon)
                .font(.system(size: 80))
                .foregroundColor(.green)
                .symbolEffect(.bounce, value: currentTaskIndex)
            
            Text(currentTask.title)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            Text(currentTask.instruction)
                .font(.body)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
            
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.3), lineWidth: 8)
                    .frame(width: 120, height: 120)
                
                Circle()
                    .trim(from: 0, to: taskProgress)
                    .stroke(Color.green, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .frame(width: 120, height: 120)
                    .rotationEffect(.degrees(-90))
                    .animation(.linear, value: taskProgress)
                
                Text("\(Int(currentTask.duration * (1 - taskProgress)))")
                    .font(.system(size: 40, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
            
            HStack(spacing: 8) {
                ForEach(0..<tasks.count, id: \.self) { index in
                    Circle()
                        .fill(index < currentTaskIndex ? Color.green : (index == currentTaskIndex ? Color.orange : Color.gray.opacity(0.3)))
                        .frame(width: 12, height: 12)
                }
            }
            
            Text(String(format: NSLocalizedString("task_progress", comment: ""), currentTaskIndex + 1, tasks.count))
                .font(.caption)
                .foregroundColor(.gray)
        }
    }
    
    private var basicRestView: some View {
        VStack(spacing: 40) {
            Image(systemName: "eye.fill")
                .font(.system(size: 100))
                .foregroundColor(.green)
                .symbolEffect(.pulse)
            
            Text(NSLocalizedString("rest_time", comment: ""))
                .font(.system(size: 36, weight: .bold))
                .foregroundColor(.white)
            
            Text(timerManager.formattedTime())
                .font(.system(size: 80, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
            
            Text(NSLocalizedString("look_away", comment: ""))
                .font(.title2)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
            
            if timerManager.config.allowUnlock {
                Button(action: {
                    timerManager.emergencyUnlock()
                }) {
                    Text(NSLocalizedString("emergency_unlock", comment: ""))
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.red.opacity(0.8))
                        .cornerRadius(10)
                }
                .padding(.top, 40)
            }
        }
    }
    
    private var guidedAccessHint: some View {
        VStack(spacing: 15) {
            HStack {
                Image(systemName: "lock.shield")
                    .foregroundColor(.yellow)
                Text(NSLocalizedString("guided_access_hint", comment: ""))
                    .font(.headline)
                    .foregroundColor(.yellow)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("1. \(NSLocalizedString("guided_access_step1", comment: ""))")
                Text("2. \(NSLocalizedString("guided_access_step2", comment: ""))")
                Text("3. \(NSLocalizedString("guided_access_step3", comment: ""))")
            }
            .font(.caption)
            .foregroundColor(.gray)
            .multilineTextAlignment(.leading)
        }
        .padding()
        .background(Color.white.opacity(0.1))
        .cornerRadius(12)
    }
    
    private func setupRestScreen() {
        requestNotificationPermission()
        
        if timerManager.config.requireHealthTask && timerManager.state == .resting {
            tasks = HealthTask.randomTasks(count: 3)
            currentTaskIndex = 0
            completedTasks = []
            startTaskTimer()
        }
    }
    
    private func cleanupRestScreen() {
        taskTimer?.invalidate()
        taskTimer = nil
    }
    
    private func startTaskTimer() {
        guard currentTaskIndex < tasks.count else { return }
        
        let currentTask = tasks[currentTaskIndex]
        let totalDuration = Double(currentTask.duration)
        var elapsed: Double = 0
        
        taskProgress = 0
        
        taskTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { timer in
            elapsed += 0.1
            taskProgress = elapsed / totalDuration
            
            if taskProgress >= 1.0 {
                completeCurrentTask()
                timer.invalidate()
            }
        }
    }
    
    private func completeCurrentTask() {
        completedTasks.insert(currentTaskIndex)
        
        withAnimation {
            showCompletionAnimation = true
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            showCompletionAnimation = false
            currentTaskIndex += 1
            
            if currentTaskIndex < tasks.count {
                startTaskTimer()
            } else {
                allTasksCompleted()
            }
        }
    }
    
    private func allTasksCompleted() {
        taskTimer?.invalidate()
        taskTimer = nil
        
        if timerManager.remainingSeconds <= 0 {
            timerManager.showRestScreen = false
            timerManager.startWorkCycle()
        }
    }
    
    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }
}

#Preview {
    RestScreenView(timerManager: TimerManager())
}
