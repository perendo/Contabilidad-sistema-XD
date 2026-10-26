import AppBar from '@mui/material/AppBar'
import Container from '@mui/material/Container'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import { Navigate, Route, Routes } from 'react-router-dom'
import EntidadesPage from './pages/EntidadesPage.tsx'

function App() {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="h1">
            Sistema Contable ONG
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/entidades" replace />} />
          <Route path="/entidades" element={<EntidadesPage />} />
        </Routes>
      </Container>
    </>
  )
}

export default App
