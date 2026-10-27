import { useState } from 'react'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import GroupIcon from '@mui/icons-material/Group'
import LogoutIcon from '@mui/icons-material/Logout'
import MenuIcon from '@mui/icons-material/Menu'
import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import Divider from '@mui/material/Divider'
import Drawer from '@mui/material/Drawer'
import IconButton from '@mui/material/IconButton'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import useMediaQuery from '@mui/material/useMediaQuery'
import { useTheme } from '@mui/material/styles'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { NOMBRES_ROL, useSesion } from '../sesion.tsx'

const ANCHO_MENU = 240

type Seccion = { texto: string; ruta: string; icono: JSX.Element; soloAdmin?: boolean }

const SECCIONES: Seccion[] = [
  { texto: 'Entidades', ruta: '/entidades', icono: <AccountBalanceIcon /> },
  { texto: 'Usuarios', ruta: '/usuarios', icono: <GroupIcon />, soloAdmin: true },
]

function MarcoApp() {
  const { usuario, cerrarSesion } = useSesion()
  const tema = useTheme()
  const esMovil = useMediaQuery(tema.breakpoints.down('md'))
  const ubicacion = useLocation()
  const navegar = useNavigate()
  const [menuAbierto, setMenuAbierto] = useState(false)

  const irA = (ruta: string) => {
    navegar(ruta)
    setMenuAbierto(false)
  }

  const seccionesVisibles = SECCIONES.filter((seccion) => {
    if (!seccion.soloAdmin) return true
    return usuario?.rol.nombre === 'administrador'
  })

  const menu = (
    <>
      <Toolbar />
      <Divider />
      <List>
        {seccionesVisibles.map((seccion) => (
          <ListItemButton
            key={seccion.ruta}
            selected={ubicacion.pathname.startsWith(seccion.ruta)}
            onClick={() => irA(seccion.ruta)}
          >
            <ListItemIcon>{seccion.icono}</ListItemIcon>
            <ListItemText primary={seccion.texto} />
          </ListItemButton>
        ))}
      </List>
    </>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{ zIndex: (estilos) => estilos.zIndex.drawer + 1 }}>
        <Toolbar>
          {esMovil && (
            <IconButton
              color="inherit"
              edge="start"
              aria-label="Abrir menú"
              onClick={() => setMenuAbierto(true)}
              sx={{ mr: 1 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" component="h1" noWrap sx={{ flexGrow: 1, minWidth: 0 }}>
            Sistema Contable ONG
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ textAlign: 'right', maxWidth: { xs: 110, sm: 240 } }}>
              <Typography variant="body2" noWrap>
                {usuario?.nombre_completo}
              </Typography>
              <Typography variant="caption" color="inherit" noWrap sx={{ display: 'block', opacity: 0.8 }}>
                {usuario && NOMBRES_ROL[usuario.rol.nombre]}
              </Typography>
            </Box>
            <Button color="inherit" startIcon={<LogoutIcon />} onClick={cerrarSesion}>
              Salir
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        variant={esMovil ? 'temporary' : 'permanent'}
        open={esMovil ? menuAbierto : true}
        onClose={() => setMenuAbierto(false)}
        sx={{ width: ANCHO_MENU, flexShrink: 0, '& .MuiDrawer-paper': { width: ANCHO_MENU, boxSizing: 'border-box' } }}
      >
        {menu}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, minWidth: 0 }}>
        <Toolbar />
        <Container maxWidth="md" sx={{ py: 4 }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  )
}

export default MarcoApp
