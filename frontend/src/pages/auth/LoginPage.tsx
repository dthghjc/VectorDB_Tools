import { useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAppDispatch, useAppSelector } from "@/store/hooks"
import { loginUser, clearError } from "@/store/slices/authSlice"
import { LoginForm, type LoginFormData } from "@/components/features/auth/login-form"

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useAppDispatch()
  const { isLoading, error, isAuthenticated } = useAppSelector(state => state.auth)

  // 页面级副作用：清除错误信息
  useEffect(() => {
    dispatch(clearError())
  }, [dispatch])

  // 页面级副作用：登录成功后重定向到原来的页面或首页
  useEffect(() => {
    if (isAuthenticated) {
      // 获取重定向目标：原来的页面或默认首页
      const from = location.state?.from?.pathname || '/'
      console.log('登录成功，重定向到:', from)
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, location.state])

  // 页面级业务逻辑：处理登录提交
  const handleSubmit = async (data: LoginFormData) => {
    console.log('LoginPage: Submitting login:', { email: data.email, password: '***' })
    dispatch(loginUser(data))
  }

  // 页面组装：将状态和逻辑传递给UI组件
  return (
    <LoginForm 
      onSubmit={handleSubmit}
      error={error}
      loading={isLoading}
    />
  )
}