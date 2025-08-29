import { LoginForm } from '@/components/features/auth/login-form';

export default function LoginPage() {
  // 因为布局和居中已经由 AuthLayout.tsx 负责，
  // 这个页面组件的职责就变得非常简单：直接渲染 LoginForm 即可。
  return <LoginForm />;
}