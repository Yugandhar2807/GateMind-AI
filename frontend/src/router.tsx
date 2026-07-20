import { createBrowserRouter, Navigate } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import LoginPage from '@/routes/auth/LoginPage'
import RegisterPage from '@/routes/auth/RegisterPage'
import DashboardPage from '@/routes/DashboardPage'
import RoadmapPage from '@/routes/RoadmapPage'
import TopicPage from '@/routes/TopicPage'
import PracticePage from '@/routes/PracticePage'
import MocksPage from '@/routes/MocksPage'
import AnalyticsPage from '@/routes/AnalyticsPage'
import MentorPage from '@/routes/MentorPage'
import FlashcardsPage from '@/routes/FlashcardsPage'
import NotesPage from '@/routes/NotesPage'
import BookmarksPage from '@/routes/BookmarksPage'
import SettingsPage from '@/routes/SettingsPage'

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'roadmap', element: <RoadmapPage /> },
      { path: 'roadmap/topics/:topicId', element: <TopicPage /> },
      { path: 'practice', element: <PracticePage /> },
      { path: 'mocks', element: <MocksPage /> },
      { path: 'analytics', element: <AnalyticsPage /> },
      { path: 'mentor', element: <MentorPage /> },
      { path: 'flashcards', element: <FlashcardsPage /> },
      { path: 'notes', element: <NotesPage /> },
      { path: 'bookmarks', element: <BookmarksPage /> },
      { path: 'settings', element: <SettingsPage /> },
    ],
  },
  { path: '*', element: <Navigate to="/dashboard" replace /> },
])
