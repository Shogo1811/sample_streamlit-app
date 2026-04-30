import { Component, ReactNode } from "react";
import { Box, Typography, Button, Alert } from "@mui/material";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
          gap={2}
        >
          <Alert severity="error">
            <Typography variant="h6">予期しないエラーが発生しました</Typography>
          </Alert>
          <Button
            variant="contained"
            onClick={() => window.location.reload()}
          >
            ページを再読み込み
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
