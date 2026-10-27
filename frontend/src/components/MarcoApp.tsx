import { useState } from 'react'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import AccountTreeIcon from '@mui/icons-material/AccountTree'
import BookIcon from '@mui/icons-material/Book'
import GroupIcon from '@mui/icons-material/Group'
import LogoutIcon from '@mui/icons-material/Logout'
import MenuIcon from '@mui/icons-material/Menu'
import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import Divider from '@mui/material/Divider'
import Drawer from '@mui/material/Drawer'
import FormControl from '@mui/material/FormControl'
import IconButton from '@mui/material/IconButton'
import InputLabel from '@mui/material/InputLabel'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import MenuItem from '@mui/material/MenuItem'
import Select from '@mui/material/Select'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import useMediaQuery from '@mui/material/useMediaQuery'
import { useTheme } from '@mui/material/styles'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { NOMBRES_ROL, useSesion } from '../sesion.tsx'

const ANCHO_MENU = 240

type Seccion = { texto: string; ruta: string; icono: JSX.Element; soloAdmin?: boolean; requiereContexto?: boolean; soloTesoreroOAdmin?: boolean }

const SECCIONES: Seccion[] = [
  { texto: 'Entidades', ruta: '/entidades', icono: <AccountBalanceIcon /> },
  { texto: 'Cuadro de cuentas', ruta: '/cuentas-base', icono: <AccountTreeIcon />, soloTesoreroOAdmin: true },
  { texto: 'Diario / Asientos', ruta: '/asientos', icono: <BookIcon />, requiereContexto: true, soloTesoreroOAdmin: true },
  { texto: 'Usuarios', ruta: '/usuarios', icono: <GroupIcon />, soloAdmin: true },
]

function MarcoApp() {
  const {
    usuario,
    cerrarSesion,
    entidades,
    entidadSeleccionadaId,
    ejercicioSeleccionadoId,
    establecerEntidad,
    establecerEjercicio,
    entidadSeleccionada,
  } = useSesion()
  const tema = useTheme()
  const esMovil = useMediaQuery(tema.breakpoints.down('md'))
  const ubicacion = useLocation()
  const navegar = useNavigate()
  const [menuAbierto, setMenuAbierto] = useState(false)

  const irA = (ruta: string) => {
    navegar(ruta)
    setMenuAbierto(false)
  }

  const puedeTesoreroOAdmin = usuario?.rol.nombre === 'administrador' || usuario?.rol.nombre === 'tesorero'
  const tieneContexto = Boolean(entidadSeleccionadaId && ejercicioSeleccionadoId)

  const seccionesVisibles = SECCIONES.filter((seccion) => {
    if (seccion.soloAdmin && usuario?.rol.nombre !== 'administrador') return false
    if (seccion.soloTesoreroOAdmin && !puedeTesoreroOAdmin) return false
    if (seccion.requiereContexto && !tieneContexto) return false
    return true
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
          <Typography variant="h6" component="h1" noWrap sx={{ mr: 2 }}>
            Sistema Contable ONG
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1, minWidth: 0, flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 200, bgcolor: 'rgba(255,255,255,0.12)', borderRadius: 1 }}>
              <InputLabel id="selector-entidad" sx={{ color: 'inherit' }}>
                Entidad
              </InputLabel>
              <Select
                labelId="selector-entidad"
                label="Entidad"
                value={entidadSeleccionadaId ?? ''}
                onChange={(evento) => establecerEntidad(evento.target.value || null)}
                sx={{ color: 'inherit', '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.5)' }, '.MuiSvgIcon-root': { color: 'inherit' } }}
              >
                {entidades.map((entidad) => (
                  <MenuItem key={entidad.id} value={entidad.id}>
                    {entidad.nombre}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 140, bgcolor: 'rgba(255,255,255,0.12)', borderRadius: 1 }} disabled={!entidadSeleccionada}>
              <InputLabel id="selector-ejercicio" sx={{ color: 'inherit' }}>
                Ejercicio
              </InputLabel>
              <Select
                labelId="selector-ejercicio"
                label="Ejercicio"
                value={ejercicioSeleccionadoId ?? ''}
                onChange={(evento) => establecerEjercicio(evento.target.value || null)}
                sx={{ color: 'inherit', '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.5)' }, '.MuiSvgIcon-root': { color: 'inherit' } }}
              >
                {(entidadSeleccionada?.ejercicios ?? []).map((ejercicio) => (
                  <MenuItem key={ejercicio.id} value={ejercicio.id}>
                    {ejercicio.anio}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
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
