import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import CommitteesPage from './pages/CommitteesPage';
import BillsPage from './pages/BillsPage';
import MembersPage from './pages/MembersPage';
import Nav from './components/Nav';
import './App.css';

const App = () => {
  return (
    <Router>
      <div>
        <Nav />
        <Routes>
          <Route path="/committees" element={<CommitteesPage />} />
          <Route path="/bills" element={<BillsPage />} />
          <Route path="/members" element={<MembersPage />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;