import { useState } from 'react';
import { AnimatePresence } from 'motion/react';
import { Layout, type TabId } from './components/Layout';
import { DashboardScreen } from './screens/DashboardScreen';
import { CareMazeScreen } from './screens/CareMazeScreen';
import { MedicationHubScreen } from './screens/MedicationHubScreen';
import { HistoryScreen } from './screens/HistoryScreen';
import { HITLScreen } from './screens/HITLScreen';
import { LoginScreen } from './screens/LoginScreen';
import { AboutScreen } from './screens/AboutScreen';
import { MarketplaceScreen } from './screens/MarketplaceScreen';
import { VoiceAssistant } from './components/VoiceAssistant';
import { ChatAssistant } from './components/ChatAssistant';
import { useWorkspace } from './hooks/useWorkspace';
import { DoctorWorkspaceScreen } from './screens/DoctorWorkspaceScreen';

export default function App() {
  const [loggedInPatientId, setLoggedInPatientId] = useState<number | null>(() => {
    const stored = localStorage.getItem('curequest_patient_id');
    return stored ? Number(stored) : null;
  });

  const [role, setRole] = useState<'patient' | 'doctor'>('patient');

  const handleLogin = (patientId: number) => {
    localStorage.setItem('curequest_patient_id', String(patientId));
    setLoggedInPatientId(patientId);
  };

  if (loggedInPatientId === null) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  if (role === 'doctor') {
    return <DoctorWorkspaceScreen patientId={loggedInPatientId} onRoleChange={() => setRole('patient')} />;
  }

  return <AuthenticatedApp patientId={loggedInPatientId} onRoleChange={() => setRole('doctor')} />;
}

function AuthenticatedApp({ patientId: initialPatientId, onRoleChange }: { patientId: number, onRoleChange: () => void }) {
  const [activeTab, setActiveTab] = useState<TabId>('dashboard');
  const { workspace, loading, error, refresh, patientId } = useWorkspace(initialPatientId);

  const renderScreen = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardScreen workspace={workspace} loading={loading} error={error} onRefresh={refresh} />;
      case 'care-maze':
        return <CareMazeScreen workspace={workspace} loading={loading} onRefresh={refresh} patientId={patientId} />;
      case 'medications':
        return <MedicationHubScreen workspace={workspace} loading={loading} onRefresh={refresh} patientId={patientId} />;
      case 'marketplace':
        return <MarketplaceScreen />;
      case 'hitl':
        return <HITLScreen workspace={workspace} loading={loading} onRefresh={refresh} patientId={patientId} />;
      case 'history':
        return <HistoryScreen workspace={workspace} loading={loading} error={error} />;
      case 'about':
        return <AboutScreen workspace={workspace} loading={loading} error={error} onRefresh={refresh} />;
      default:
        return <DashboardScreen workspace={workspace} loading={loading} error={error} onRefresh={refresh} />;
    }
  };

  return (
    <Layout
      activeTab={activeTab}
      onTabChange={setActiveTab}
      patientName={workspace?.patient.full_name ?? 'your care circle'}
      onRefresh={refresh}
      loading={loading}
      onRoleChange={onRoleChange}
    >
      <AnimatePresence mode="wait">
        <div key={activeTab} className="min-h-full min-w-0 w-full">
          {renderScreen()}
        </div>
      </AnimatePresence>
      <ChatAssistant patientId={patientId} />
      <VoiceAssistant patientId={patientId} />
    </Layout>
  );
}
