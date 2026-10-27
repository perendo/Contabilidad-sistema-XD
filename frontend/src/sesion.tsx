import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { CLAVE_SESION, cliente, EVENTO_SESION_CADUCADA } from './api/cliente.ts'

export type Rol = 'administrador' | 'tesorero' | 'solo_lectura'

export const NOMBRES_ROL: Record<Rol, string> = {
  administrador: 'Administración',
  tesorero: 'Tesorería',
  solo_lectura: 'Solo lectura',
}

export type UsuarioSesion = {
  id: string
  email: string
  nombre_completo: string
  rol: { nombre: Rol }
}

export type Ejercicio = {
  id: string
  anio: number
  fecha_inicio: string
  fecha_fin: string
  cerrado: boolean
}

export type Entidad = {
  id: string
  cif: string
  nombre: string
  activa: boolean
  creada_en: string
  ejercicios: Ejercicio[]
}

type ContextoSesion = {
  usuario: UsuarioSesion | null
  cargando: boolean
  aviso: string
  iniciarSesion: (email: string, password: string) => Promise<void>
  cerrarSesion: () => void
  entidades: Entidad[]
  entidadSeleccionadaId: string | null
  ejercicioSeleccionadoId: string | null
  establecerEntidad: (entidadId: string | null) => void
  establecerEjercicio: (ejercicioId: string | null) => void
  cargarEntidades: () => Promise<void>
  entidadSeleccionada: Entidad | null
  ejercicioSeleccionado: Ejercicio | null
}

const CLAVE_ENTIDAD = 'entidad_seleccionada'
const CLAVE_EJERCICIO = 'ejercicio_seleccionado'

const SesionContext = createContext<ContextoSesion | null>(null)

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null)
  const [cargando, setCargando] = useState(true)
  const [aviso, setAviso] = useState('')
  const [entidades, setEntidades] = useState<Entidad[]>([])
  const [entidadSeleccionadaId, setEntidadSeleccionadaId] = useState<string | null>(() =>
    sessionStorage.getItem(CLAVE_ENTIDAD),
  )
  const [ejercicioSeleccionadoId, setEjercicioSeleccionadoId] = useState<string | null>(() =>
    sessionStorage.getItem(CLAVE_EJERCICIO),
  )

  useEffect(() => {
    if (!sessionStorage.getItem(CLAVE_SESION)) {
      setCargando(false)
      return
    }
    cliente
      .get<UsuarioSesion>('/auth/me')
      .then(({ data }) => setUsuario(data))
      .catch(() => undefined)
      .finally(() => setCargando(false))
  }, [])

  useEffect(() => {
    const alCaducar = () => {
      setUsuario(null)
      setAviso('Tu sesión ha caducado o no es válida. Vuelve a entrar.')
      setEntidades([])
      setEntidadSeleccionadaId(null)
      setEjercicioSeleccionadoId(null)
      sessionStorage.removeItem(CLAVE_ENTIDAD)
      sessionStorage.removeItem(CLAVE_EJERCICIO)
    }
    window.addEventListener(EVENTO_SESION_CADUCADA, alCaducar)
    return () => window.removeEventListener(EVENTO_SESION_CADUCADA, alCaducar)
  }, [])

  const cargarEntidades = useCallback(async () => {
    const { data } = await cliente.get<Entidad[]>('/entidades')
    setEntidades(data)
  }, [])

  useEffect(() => {
    if (usuario) {
      cargarEntidades().catch(() => undefined)
    }
  }, [usuario, cargarEntidades])

  const entidadSeleccionada = useMemo(
    () => entidades.find((entidad) => entidad.id === entidadSeleccionadaId) ?? null,
    [entidades, entidadSeleccionadaId],
  )

  const ejercicioSeleccionado = useMemo(
    () => entidadSeleccionada?.ejercicios.find((ejercicio) => ejercicio.id === ejercicioSeleccionadoId) ?? null,
    [entidadSeleccionada, ejercicioSeleccionadoId],
  )

  useEffect(() => {
    if (entidadSeleccionadaId && !entidadSeleccionada) {
      setEntidadSeleccionadaId(null)
      sessionStorage.removeItem(CLAVE_ENTIDAD)
    }
  }, [entidadSeleccionadaId, entidadSeleccionada])

  useEffect(() => {
    if (entidadSeleccionada) {
      if (ejercicioSeleccionadoId && !ejercicioSeleccionado) {
        setEjercicioSeleccionadoId(null)
        sessionStorage.removeItem(CLAVE_EJERCICIO)
        return
      }
      if (!ejercicioSeleccionadoId && entidadSeleccionada.ejercicios.length > 0) {
        const ejercicio = entidadSeleccionada.ejercicios[0]
        setEjercicioSeleccionadoId(ejercicio.id)
        sessionStorage.setItem(CLAVE_EJERCICIO, ejercicio.id)
      }
    } else {
      if (ejercicioSeleccionadoId) {
        setEjercicioSeleccionadoId(null)
        sessionStorage.removeItem(CLAVE_EJERCICIO)
      }
    }
  }, [entidadSeleccionada, ejercicioSeleccionadoId, ejercicioSeleccionado])

  const establecerEntidad = useCallback((entidadId: string | null) => {
    setEntidadSeleccionadaId(entidadId)
    if (entidadId) {
      sessionStorage.setItem(CLAVE_ENTIDAD, entidadId)
    } else {
      sessionStorage.removeItem(CLAVE_ENTIDAD)
    }
    setEjercicioSeleccionadoId(null)
    sessionStorage.removeItem(CLAVE_EJERCICIO)
  }, [])

  const establecerEjercicio = useCallback((ejercicioId: string | null) => {
    setEjercicioSeleccionadoId(ejercicioId)
    if (ejercicioId) {
      sessionStorage.setItem(CLAVE_EJERCICIO, ejercicioId)
    } else {
      sessionStorage.removeItem(CLAVE_EJERCICIO)
    }
  }, [])

  const iniciarSesion = useCallback(async (email: string, password: string) => {
    const { data } = await cliente.post<{ access_token: string }>('/auth/login', { email, password })
    sessionStorage.setItem(CLAVE_SESION, data.access_token)
    try {
      const { data: yo } = await cliente.get<UsuarioSesion>('/auth/me')
      setUsuario(yo)
      setAviso('')
    } catch (fallo) {
      sessionStorage.removeItem(CLAVE_SESION)
      throw fallo
    }
  }, [])

  const cerrarSesion = useCallback(() => {
    sessionStorage.removeItem(CLAVE_SESION)
    setUsuario(null)
    setAviso('')
    setEntidades([])
    setEntidadSeleccionadaId(null)
    setEjercicioSeleccionadoId(null)
    sessionStorage.removeItem(CLAVE_ENTIDAD)
    sessionStorage.removeItem(CLAVE_EJERCICIO)
  }, [])

  const valor = useMemo(
    () => ({
      usuario,
      cargando,
      aviso,
      iniciarSesion,
      cerrarSesion,
      entidades,
      entidadSeleccionadaId,
      ejercicioSeleccionadoId,
      establecerEntidad,
      establecerEjercicio,
      cargarEntidades,
      entidadSeleccionada,
      ejercicioSeleccionado,
    }),
    [
      usuario,
      cargando,
      aviso,
      iniciarSesion,
      cerrarSesion,
      entidades,
      entidadSeleccionadaId,
      ejercicioSeleccionadoId,
      establecerEntidad,
      establecerEjercicio,
      cargarEntidades,
      entidadSeleccionada,
      ejercicioSeleccionado,
    ],
  )

  return <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>
}

export function useSesion() {
  const contexto = useContext(SesionContext)
  if (contexto === null) {
    throw new Error('useSesion debe usarse dentro de ProveedorSesion')
  }
  return contexto
}
