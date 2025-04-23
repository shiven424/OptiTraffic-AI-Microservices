import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { styled, lighten, darken } from '@mui/material/styles';

// Helper: Get background colour based on event type and theme with new mappings
const getNotificationColor = (notification, darkMode) => {
  if (!notification || !notification.event) return darkMode ? "#1e1e1e" : "#f9f9f9";
  const type = notification.event.event_type;
  if (type === 'accident') return darkMode ? "#b71c1c" : "#ffcdd2";      
  if (type === 'congestion') return darkMode ? "#f9a825" : "#fff176";      
  if (type === 'light_failure') return darkMode ? "#0d47a1" : "#bbdefb";     
  return darkMode ? "#1e1e1e" : "#f9f9f9";
};

const NotificationCard = styled(Card)(({ theme, darkMode, bgcolor }) => {
  const baseColor = bgcolor || (darkMode ? '#1e1e1e' : '#f9f9f9');
  return {
    backgroundColor: baseColor,
    color: darkMode ? '#fff' : '#000',
    borderRadius: theme.spacing(1),
    marginBottom: theme.spacing(2),
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: darkMode ? lighten(baseColor, 0.3) : darken(baseColor, 0.1),
    },
  };
});

const formatEventType = (type) => {
  if (!type) return '';
  if (type === 'light_failure') return 'Light Failure';
  return type.charAt(0).toUpperCase() + type.slice(1);
};

const NotificationPanel = ({ darkMode }) => {
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('All');
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

  const fetchNotifications = () => {
    const token = localStorage.getItem("access_token");
      fetch(`${API_URL}/notifications/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => setNotifications(data))
      .catch((error) => console.error("Error fetching notifications:", error));
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 5000);
    return () => clearInterval(interval);
  }, []);

  // Filter notifications if a filter is selected.
  const filteredNotifications =
    filter === 'All'
      ? notifications
      : notifications.filter(
          (n) => n.event && n.event.event_type === filter
        );

  return (
    <Box
      sx={{
        p: 3,
        m: 3,
        ml: '370px',  
        mr: '320px',  
        bgcolor: darkMode ? '#121212' : '#ffffff',
        color: darkMode ? '#ffffff' : '#000000',
        borderRadius: 2,
        boxShadow: 3,
        maxHeight: '80vh',
        overflowY: 'auto',
      }}
    >
      {/* Header with Title, Refresh Button and Filter Bar */}
      <Box display="flex" flexDirection="column" mb={2}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h5">Notifications</Typography>
          <Button
            variant="outlined"
            onClick={fetchNotifications}
            startIcon={<RefreshIcon />}
            sx={{
              borderColor: darkMode ? '#fff' : '#000',
              color: darkMode ? '#fff' : '#000',
            }}
          >
            Refresh
          </Button>
        </Box>
        <Box display="flex" alignItems="center">
          <Typography variant="subtitle2" sx={{ mr: 2 }}>
            Filter by Event Type:
          </Typography>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
            <InputLabel id="event-filter-label">Event Type</InputLabel>
            <Select
              labelId="event-filter-label"
              value={filter}
              label="Event Type"
              onChange={(e) => setFilter(e.target.value)}
            >
              <MenuItem value="All">All</MenuItem>
              <MenuItem value="accident">Accident</MenuItem>
              <MenuItem value="light_failure">Light Failure</MenuItem>
              <MenuItem value="congestion">Congestion</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>
      <Divider sx={{ mb: 2 }} />

      {/* Notification Cards Grid */}
      <Grid container spacing={2}>
        {filteredNotifications.length === 0 ? (
          <Grid item xs={12}>
            <Typography variant="body1" align="center">
              No notifications available.
            </Typography>
          </Grid>
        ) : (
          filteredNotifications.map((notification, index) => {
            const bgColor = getNotificationColor(notification, darkMode);
            return (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <NotificationCard darkMode={darkMode} bgcolor={bgColor}>
                  <CardHeader
                    title={
                      <Typography variant="h6">
                        {notification.event
                          ? formatEventType(notification.event.event_type)
                          : 'Unknown Event'}
                      </Typography>
                    }
                    subheader={notification.timestamp || '-'}
                  />
                  <CardContent>
                    <Typography variant="body2">
                      <strong>Target Type:</strong>{' '}
                      {notification.event ? notification.event.target_type : '-'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Target ID:</strong>{' '}
                      {notification.event ? notification.event.target_id : '-'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Email Sent To:</strong> {notification.email_sent_to || '-'}
                    </Typography>
                  </CardContent>
                </NotificationCard>
              </Grid>
            );
          })
        )}
      </Grid>
    </Box>
  );
};

export default NotificationPanel;
