import AuthForm from "../components/AuthForm";

type LoginProps = {
  onAuthenticated: (token: string) => void;
};

export default function Login({ onAuthenticated }: LoginProps) {
  return <AuthForm mode="login" onAuthenticated={onAuthenticated} />;
}
