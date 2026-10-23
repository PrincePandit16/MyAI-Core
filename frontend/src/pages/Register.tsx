import AuthForm from "../components/AuthForm";

type RegisterProps = {
  onAuthenticated: (token: string) => void;
};

export default function Register({ onAuthenticated }: RegisterProps) {
  return <AuthForm mode="register" onAuthenticated={onAuthenticated} />;
}
