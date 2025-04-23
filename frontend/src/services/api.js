const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';
const MONITORING_API_URL = API_URL;

export const fetchTrafficData = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${API_URL}/api/traffic/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return await response.json();
  } catch (error) {
    console.error('Error fetching traffic data:', error);
    return null;
  }
};

export const fetchMonitoringData = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${MONITORING_API_URL}/api/monitoring/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return await response.json();
  } catch (error) {
    console.error('Error fetching monitoring data:', error);
    return null;
  }
};
