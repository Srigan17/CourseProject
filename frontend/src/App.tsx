import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { HospitalNetworkPage } from './pages/HospitalNetworkPage';
import { ModelTrainingPage } from './pages/ModelTrainingPage';
import { PatientActivityTestingPage } from './pages/PatientActivityTestingPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { apiClient } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isTraining, setIsTraining] = useState(false);

  // Initial load and periodic training check
  useEffect(() => {
    refreshStatus();
    const interval = setInterval(async () => {
      try {
        const s = await apiClient.getTrainingStatus();
        setIsTraining(s.is_training);
      } catch (err) {
        // quiet fallback
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const refreshStatus = async () => {
    setIsRefreshing(true);
    try {
      const s = await apiClient.getTrainingStatus();
      setIsTraining(s.is_training);
    } catch (err) {
      // quiet fallback in demo mode
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900 antialiased">
      {/* 5-item Navy Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isTraining={isTraining}
      />

      {/* Main Layout Area */}
      <div className="flex-1 ml-64 flex flex-col min-w-0">
        <Header
          activeTab={activeTab}
          onRefresh={refreshStatus}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 p-6 lg:p-8">
          {activeTab === 'overview' && (
            <DashboardPage onNavigate={setActiveTab} />
          )}

          {activeTab === 'network' && (
            <HospitalNetworkPage />
          )}

          {activeTab === 'training' && (
            <ModelTrainingPage onNavigateToResults={() => setActiveTab('performance')} />
          )}

          {activeTab === 'testing' && (
            <PatientActivityTestingPage />
          )}

          {activeTab === 'performance' && (
            <ModelPerformancePage />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;