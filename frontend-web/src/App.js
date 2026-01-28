import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_BASE = 'http://127.0.0.1:8000/api';

// Configure axios defaults
axios.defaults.headers.post['Content-Type'] = 'application/json';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('v_auth'));
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');

  const fetchHistory = useCallback(async (authOverride) => {
    const token = authOverride || localStorage.getItem('v_auth');
    if (!token) return;

    try {
      const response = await axios.get(`${API_BASE}/history/`, {
        headers: { 'Authorization': `Token ${token}` }
      });
      setHistory(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        handleLogout();
      }
      console.error('History fetch error:', error);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchHistory();
    }
  }, [isAuthenticated, fetchHistory]);

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    // REMOVED withCredentials - this was causing CORS issues
    axios.post(`${API_BASE}/login/`, credentials)
    .then(res => {
      if (res.data && res.data.token) {
        localStorage.setItem('v_auth', res.data.token);
        setIsAuthenticated(true);
        setCredentials({ username: '', password: '' });
        // Fetch history immediately after login with the new token
        fetchHistory(res.data.token);
      } else {
        setError('Invalid response from server');
      }
    })
    .catch((err) => {
      console.error('Login error:', err);
      if (err.response) {
        setError(err.response?.data?.error || 'Invalid credentials');
      } else if (err.request) {
        setError('Cannot connect to server. Is the backend running?');
      } else {
        setError('An unexpected error occurred');
      }
    })
    .finally(() => setLoading(false));
  };

  const handleLogout = () => {
    const token = localStorage.getItem('v_auth');
    
    // Optional: Call logout endpoint to delete token on server
    if (token) {
      axios.post(`${API_BASE}/logout/`, {}, {
        headers: { 'Authorization': `Token ${token}` }
      }).catch(err => console.error('Logout error:', err));
    }
    
    localStorage.removeItem('v_auth');
    setIsAuthenticated(false);
    setData(null);
    setHistory([]);
    setError('');
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const token = localStorage.getItem('v_auth');
    if (!token) {
      setError('Not authenticated');
      handleLogout();
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE}/upload/`, formData, {
        headers: { 
          'Authorization': `Token ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data) {
        setData(response.data);
        fetchHistory();
      }
    } catch (error) {
      if (error.response?.status === 401) {
        setError('Session expired. Please login again.');
        handleLogout();
      } else {
        setError(error.response?.data?.error || 'Upload failed. Verify CSV format.');
      }
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
      // Reset file input
      e.target.value = null;
    }
  };

  const handleDownloadPDF = async () => {
    const token = localStorage.getItem('v_auth');
    if (!token) {
      setError('Not authenticated');
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/download-pdf/`, {
        headers: { 'Authorization': `Token ${token}` },
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `VISTA_Report_${new Date().getTime()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      if (error.response?.status === 401) {
        setError('Session expired. Please login again.');
        handleLogout();
      } else {
        setError('PDF generation failed.');
      }
      console.error('PDF download error:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <div className="bg-slate-900 border border-slate-800 p-10 rounded-[2.5rem] w-full max-w-md shadow-2xl">
          <h2 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-2">V.I.S.T.A.</h2>
          <p className="text-slate-500 text-xs uppercase tracking-widest mb-8 font-bold">Secure Gateway</p>
          {error && <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-400 text-xs">{error}</div>}
          <form onSubmit={handleLogin} className="space-y-4">
            <input 
              type="text" 
              placeholder="Username" 
              autoComplete="username"
              value={credentials.username}
              className="w-full bg-slate-800 border border-slate-700 p-4 rounded-xl text-white outline-none focus:border-blue-500 transition-all"
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
            />
            <input 
              type="password" 
              placeholder="Password" 
              autoComplete="current-password"
              value={credentials.password}
              className="w-full bg-slate-800 border border-slate-700 p-4 rounded-xl text-white outline-none focus:border-blue-500 transition-all"
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            />
            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 py-4 rounded-xl font-bold text-white transition-all mt-4 uppercase"
            >
              {loading ? "Verifying..." : "Initialize Session"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  const chartData = data && data.averages ? {
    labels: ['Flowrate', 'Pressure', 'Temp'],
    datasets: [{
      label: 'System Metrics',
      data: [
        data.averages.avg_flowrate || 0, 
        data.averages.avg_pressure || 0, 
        data.averages.avg_temp || 0
      ],
      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
      borderRadius: 8,
    }],
  } : null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 md:p-12 font-sans">
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-12 border-b border-slate-800 pb-8 gap-6">
        <div onClick={() => window.location.reload()} className="cursor-pointer">
          <h1 className="text-4xl font-black bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">V.I.S.T.A.</h1>
          <p className="text-slate-500 font-mono text-[10px] mt-2 uppercase tracking-[0.3em]">Hybrid Chemical Telemetry</p>
        </div>
        
        <div className="flex gap-4 items-center">
          {error && <div className="text-red-400 text-xs">{error}</div>}
          <button 
            onClick={handleDownloadPDF}
            className="px-6 py-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl font-bold text-white text-xs transition-all disabled:opacity-50"
            disabled={!data}
          >
            📄 EXPORT PDF
          </button>
          <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 transition-all px-8 py-3 rounded-xl font-bold text-white text-xs shadow-lg shadow-blue-900/20">
            {loading ? "ANALYZING..." : "UPLOAD CSV"}
            <input type="file" className="hidden" onChange={handleUpload} accept=".csv" disabled={loading} />
          </label>
          <button onClick={handleLogout} className="text-slate-500 hover:text-red-400 text-xs font-bold transition-colors">LOGOUT</button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-8">
          {data ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard title="Total Items" value={data.total_count || 'N/A'} />
                <MetricCard title="Avg Pressure" value={`${data.averages?.avg_pressure || 'N/A'} PSI`} color="text-emerald-400" />
                <MetricCard title="Mean Temp" value={`${data.averages?.avg_temp || 'N/A'} °C`} color="text-amber-500" />
              </div>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl">
                  <h3 className="text-sm font-bold mb-8 text-slate-500 uppercase tracking-widest">Parameter Distribution</h3>
                  <div className="h-64">
                    {chartData ? (
                      <Bar 
                        data={chartData} 
                        options={{ 
                          maintainAspectRatio: false, 
                          scales: { y: { grid: { color: '#1e293b' } }, x: { grid: { display: false } } },
                          plugins: { legend: { display: false } } 
                        }} 
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full text-slate-600">No data available</div>
                    )}
                  </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl">
                  <h3 className="text-sm font-bold mb-8 text-slate-500 uppercase tracking-widest">Asset Preview</h3>
                  <div className="overflow-y-auto max-h-64 custom-scrollbar">
                    {data.raw_data && data.raw_data.length > 0 ? (
                      <table className="w-full text-left text-xs">
                        <tbody className="divide-y divide-slate-800">
                          {data.raw_data.map((row, i) => (
                            <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                              <td className="py-3 font-bold">{row['Equipment Name'] || 'N/A'}</td>
                              <td className="py-3 text-slate-500">{row['Type'] || 'N/A'}</td>
                              <td className="py-3 text-right text-blue-400 font-mono">{row['Flowrate'] || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p className="text-slate-600 text-center py-8">No asset data available</p>
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="h-96 border-2 border-dashed border-slate-800 rounded-[3rem] flex items-center justify-center bg-slate-900/20">
              <div className="text-center">
                <div className="text-4xl mb-4">📊</div>
                <p className="text-slate-600 font-medium">Ready for data ingestion.</p>
              </div>
            </div>
          )}
        </div>

        <aside className="lg:col-span-1 bg-slate-900/50 border border-slate-800 rounded-3xl p-6 h-fit">
          <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-6 flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
            Sync History
          </h3>
          <div className="space-y-3">
            {history.length > 0 ? history.map((item, index) => (
              <div key={index} className="p-4 bg-slate-900 border border-slate-800 rounded-xl hover:border-blue-500/30 transition-all cursor-default group">
                <p className="font-bold text-xs truncate text-slate-300 group-hover:text-blue-400 transition-colors">{item.name || 'Unknown'}</p>
                <p className="text-[9px] text-slate-600 mt-1 font-mono">
                  {item.date ? new Date(item.date).toLocaleDateString() + ' // ' + new Date(item.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'No date'}
                </p>
              </div>
            )) : <p className="text-[10px] text-slate-700 italic text-center py-4">No recent activity detected</p>}
          </div>
        </aside>
      </main>
    </div>
  );
}

function MetricCard({ title, value, color = "text-white" }) {
  return (
    <div className="p-8 bg-slate-900 border border-slate-800 rounded-3xl hover:bg-slate-900/80 transition-all group">
      <p className="text-slate-500 text-[10px] font-bold uppercase mb-2 tracking-widest">{title}</p>
      <p className={`text-3xl font-black ${color} tracking-tight`}>{value || 'N/A'}</p>
    </div>
  );
}

export default App;