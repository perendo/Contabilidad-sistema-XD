import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import MarcoApp from './components/MarcoApp.tsx'
import EntidadesPage from './pages/EntidadesPage.tsx'
import LoginPage from './pages/LoginPage.tsx'
import UsuariosPage from './pages/UsuariosPage.tsx'
import { useSesion } from './sesion.tsx'

function RutaPrivada() {
  const { usuario, cargando } = useSesion()

  if (cargando) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

function RutaSoloAdmin() {
  const { usuario } = useSesion()
  if (usuario?.rol.nombre !== 'administrador') {
    return <Navigate to="/entidades" replace />
  }
  return <Outlet />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RutaPrivada />}>
        <Route element={<MarcoApp />}>
          <Route path="/entidades" element={<EntidadesPage />} />
          <Route element={<RutaSoloAdmin />}>
            <Route path="/usuarios" element={<UsuariosPage />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/entidades" replace />} />
    </Routes>
  )
}

export default App
