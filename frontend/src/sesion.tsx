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

type ContextoSesion = {
  usuario: UsuarioSesion | null
  cargando: boolean
  aviso: string
  iniciarSesion: (email: string, password: string) => Promise<void>
  cerrarSesion: () => void
}

const SesionContext = createContext<ContextoSesion | null>(null)

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null)
  const [cargando, setCargando] = useState(true)
  const [aviso, setAviso] = useState('')

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
    }
    window.addEventListener(EVENTO_SESION_CADUCADA, alCaducar)
    return () => window.removeEventListener(EVENTO_SESION_CADUCADA, alCaducar)
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
  }, [])

  const valor = useMemo(
    () => ({ usuario, cargando, aviso, iniciarSesion, cerrarSesion }),
    [usuario, cargando, aviso, iniciarSesion, cerrarSesion],
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
