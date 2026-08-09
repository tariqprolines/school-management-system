import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './redux/store';
import ProtectedRoute from './components/ProtectedRoute';
import RoleRoute from './components/RoleRoute';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TeachersPage from './pages/TeachersPage';
import TeacherDetailPage from './pages/TeacherDetailPage';
import StudentsPage from './pages/StudentsPage';
import StudentDetailPage from './pages/StudentDetailPage';
import ClassesPage from './pages/ClassesPage';
import TimetablePage from './pages/TimetablePage';
import FeesPage from './pages/FeesPage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import './index.css';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route element={<RoleRoute />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/teachers" element={<TeachersPage />} />
                <Route path="/teachers/:id" element={<TeacherDetailPage />} />
                <Route path="/students" element={<StudentsPage />} />
                <Route path="/students/:id" element={<StudentDetailPage />} />
                <Route path="/classes" element={<ClassesPage />} />
                <Route path="/timetable" element={<TimetablePage />} />
                <Route path="/fees" element={<FeesPage />} />
              </Route>
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </Provider>
  );
}

export default App;
