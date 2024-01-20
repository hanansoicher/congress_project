import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import CommitteesPage from './pages/CommitteesPage';
import CommitteeDetailsPage from './pages/CommitteeDetailsPage';
import BillsPage from './pages/BillsPage';
import MembersPage from './pages/MembersPage';
import MemberDetailsPage from './pages/MemberDetailsPage';
import Nav from './components/Nav';
import styled from 'styled-components';

// Styled Root Container
const RootContainer = styled.div`
  margin: 1rem auto;
  padding: 1rem;
  text-align: center;
`;

const App = () => {
  return (
    <Router>
      <RootContainer>
        <Nav />
        <Routes>
          <Route path="/committees" element={<CommitteesPage />} />
          <Route path="/committees/:committeeId" element={<CommitteeDetailsPage />} />
          <Route path="/bills" element={<BillsPage />} />
          <Route path="/members" element={<MembersPage />} />
          <Route path="/members/:memberId" element={<MemberDetailsPage />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </RootContainer>
    </Router>
  );
}

export default App;
