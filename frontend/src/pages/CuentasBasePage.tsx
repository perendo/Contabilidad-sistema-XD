import { useEffect, useState } from 'react'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import Paper from '@mui/material/Paper'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Typography from '@mui/material/Typography'
import { cliente } from '../api/cliente.ts'

type CuentaBase = {
  id: string
  codigo: string
  nombre: string
  descripcion: string | null
}

function CuentasBasePage() {
  const [cuentas, setCuentas] = useState<CuentaBase[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const hayDescripcion = cuentas.some((cuenta) => Boolean(cuenta.descripcion))

  useEffect(() => {
    cliente
      .get<CuentaBase[]>('/cuentas/base')
      .then(({ data }) => setCuentas(data))
      .catch(() => setError('No se pudo cargar el cuadro de cuentas base'))
      .finally(() => setCargando(false))
  }, [])

  return (
    <Paper component="section" elevation={1} sx={{ p: 3 }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Cuadro de cuentas base
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        PGC español · cuentas de hasta 3 dígitos compartidas por todas las entidades
      </Typography>

      {error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      ) : cargando ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : cuentas.length === 0 ? (
        <Typography color="text.secondary">No hay cuentas en el cuadro base.</Typography>
      ) : (
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader size="small" aria-label="Cuadro de cuentas base del PGC">
            <TableHead>
              <TableRow>
                <TableCell scope="col">Código</TableCell>
                <TableCell scope="col">Nombre</TableCell>
                {hayDescripcion && <TableCell scope="col">Descripción</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {cuentas.map((cuenta) => (
                <TableRow key={cuenta.id} hover>
                  <TableCell sx={{ fontFamily: 'monospace', whiteSpace: 'nowrap' }}>{cuenta.codigo}</TableCell>
                  <TableCell>{cuenta.nombre}</TableCell>
                  {hayDescripcion && <TableCell>{cuenta.descripcion ?? '—'}</TableCell>}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  )
}

export default CuentasBasePage
