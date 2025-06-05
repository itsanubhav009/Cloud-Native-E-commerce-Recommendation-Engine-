import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';
import { API_URL } from '../config';
import MetricCard from '../components/MetricCard';
import RecommendationTable from '../components/RecommendationTable';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalUsers: 0,
    totalProducts: 0,
    totalRecommendations: 0,
    conversionRate: 0
  });
  const [recentRecommendations, setRecentRecommendations] = useState([]);
  const [categoryDistribution, setCategoryDistribution] = useState([]);
  const [weeklyEngagement, setWeeklyEngagement] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch summary metrics
        const metricsResponse = await axios.get(`${API_URL}/api/analytics/summary`);
        setMetrics(metricsResponse.data);
        
        // Fetch recent recommendations
        const recommendationsResponse = await axios.get(`${API_URL}/api/analytics/recent-recommendations`);
        setRecentRecommendations(recommendationsResponse.data);
        
        // Fetch category distribution
        const categoryResponse = await axios.get(`${API_URL}/api/analytics/category-distribution`);
        setCategoryDistribution(categoryResponse.data);
        
        // Fetch weekly engagement
        const engagementResponse = await axios.get(`${API_URL}/api/analytics/weekly-engagement`);
        setWeeklyEngagement(engagementResponse.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Key Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Total Users" 
            value={metrics.totalUsers} 
            icon="people"
            color="#0088FE"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Total Products" 
            value={metrics.totalProducts} 
            icon="shopping_bag"
            color="#00C49F"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Recommendations" 
            value={metrics.totalRecommendations} 
            icon="recommend"
            color="#FFBB28"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Conversion Rate" 
            value={`${metrics.conversionRate}%`} 
            icon="trending_up"
            color="#FF8042"
          />
        </Grid>
      </Grid>
      
      {/* Charts */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Weekly Engagement
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={weeklyEngagement}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="views" fill="#0088FE" name="Views" />
                <Bar dataKey="purchases" fill="#00C49F" name="Purchases" />
                <Bar dataKey="recommendations" fill="#FFBB28" name="Recommendations" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Category Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {categoryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Recent Recommendations */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Recommendations
        </Typography>
        <RecommendationTable recommendations={recentRecommendations} />
      </Paper>
    </Box>
  );
};

export default Dashboard;