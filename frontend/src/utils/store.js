import { create } from 'zustand';
import toast from 'react-hot-toast';

export const useLiveStore = create((set, get) => ({
  liveActivities: [],
  employeeRiskScores: {},
  latestAlert: null,
  socket: null,
  connectionStatus: 'disconnected',
  demoModeActive: true,

  connectWebSocket: () => {
    if (get().socket) return;

    const wsUrl = `ws://${window.location.hostname}:8000/api/v1/ws`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      set({ connectionStatus: 'connected', socket });
      loggerLog("WebSocket Connected to SOC");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'simulation_tick') {
          const { activity, risk_score, alert } = data;

          // 1. Add activity to feed
          set((state) => {
            const current = [activity, ...state.liveActivities];
            return { liveActivities: current.slice(0, 50) };
          });

          // 2. Update employee risk score
          if (risk_score) {
            set((state) => ({
              employeeRiskScores: {
                ...state.employeeRiskScores,
                [risk_score.employee_id]: risk_score
              }
            }));
          }

          // 3. Handle Alert Triggering
          if (alert) {
            set({ latestAlert: alert });
            
            // Audio alert trigger
            triggerAudioAlert(alert.severity);

            // Speech Synthesis
            triggerVoiceNotification(
              `${alert.severity.toUpperCase()} alert triggered for employee ${alert.employee_name}. ${alert.title}`
            );

            // Display toast
            toast((t) => (
              <div className="flex flex-col gap-1 text-[11px]">
                <div className="font-bold flex items-center gap-1 text-red-400">
                  ⚠️ [{alert.severity.toUpperCase()}] {alert.title}
                </div>
                <div>Employee: {alert.employee_name} ({alert.department})</div>
                <div className="text-gray-400 italic mt-1 line-clamp-2">{alert.description}</div>
              </div>
            ), {
              duration: 5000,
              style: {
                background: '#0F1629',
                color: '#E8EDF5',
                border: '1px solid #FF3B5C',
                borderRadius: '12px',
                padding: '12px'
              }
            });
          }
        }
      } catch (err) {
        console.error('Error parsing live socket payload:', err);
      }
    };

    socket.onclose = () => {
      set({ connectionStatus: 'disconnected', socket: null });
      loggerLog("WebSocket Disconnected. Reconnecting in 3s...");
      setTimeout(() => get().connectWebSocket(), 3000);
    };

    socket.onerror = (err) => {
      console.error('WebSocket encountered an error:', err);
      socket.close();
    };
  },

  disconnectWebSocket: () => {
    const socket = get().socket;
    if (socket) {
      socket.close();
      set({ socket: null, connectionStatus: 'disconnected' });
    }
  },

  setDemoMode: (active) => set({ demoModeActive: active })
}));


function loggerLog(msg) {
  console.log(`%c[SOC-WS] ${msg}`, 'color: #00D9FF; font-weight: bold;');
}

// ─── Web Audio API Synthesizer ───
export function triggerAudioAlert(severity) {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    
    if (severity === 'critical') {
      // Two-tone warning siren
      const playTone = (freq, duration, start) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.08, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + duration);
        osc.start(start);
        osc.stop(start + duration);
      };
      
      const now = ctx.currentTime;
      playTone(880, 0.25, now);
      playTone(660, 0.25, now + 0.35);
    } else {
      // Single ping tone
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = 'sine';
      osc.frequency.setValueAtTime(700, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(900, ctx.currentTime + 0.15);
      gain.gain.setValueAtTime(0.06, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
      osc.start();
      osc.stop(ctx.currentTime + 0.25);
    }
  } catch (e) {
    console.error('Audio alerts failed:', e);
  }
}

// ─── Web Speech Synthesis ───
export function triggerVoiceNotification(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel(); // Terminate existing speaker queue
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 0.95;
    window.speechSynthesis.speak(utterance);
  }
}
