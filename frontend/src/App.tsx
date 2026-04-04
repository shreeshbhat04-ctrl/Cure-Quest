import { useState } from 'react';
import { AnimatePresence } from 'motion/react';
import { Layout, type TabId } from './components/Layout';
import { DashboardScreen } from './screens/DashboardScreen';
import { CareMazeScreen } from './screens/CareMazeScreen';
import { MedicationHubScreen } from './screens/MedicationHubScreen';
import { HistoryScreen } from './screens/HistoryScreen';
import { useWorkspace } from './hooks/useWorkspace';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('dashboard');
  const { workspace, loading, error, refresh, patientId } = useWorkspace();

  const renderScreen = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardScreen workspace={workspace} loading={loading} error={error} onRefresh={refresh} />;
      case 'care-maze':
        return <CareMazeScreen workspace={workspace} loading={loading} onRefresh={refresh} patientId={patientId} />;
      case 'medications':
        return <MedicationHubScreen workspace={workspace} loading={loading} onRefresh={refresh} patientId={patientId} />;
      case 'history':
        return <HistoryScreen workspace={workspace} loading={loading} error={error} />;
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
    >
      <AnimatePresence mode="wait">
        <div key={activeTab}>{renderScreen()}</div>
      </AnimatePresence>
    </Layout>
  );
}
