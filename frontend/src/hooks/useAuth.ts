import { useQuery } from "@tanstack/react-query";
import { fetchMe, fetchConsentStatus } from "@/services/api";
import { ROLE_MANAGER, ROLE_DRIVER } from "@/types";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: fetchMe,
    staleTime: 5 * 60 * 1000, // 5分
  });
}

export function useConsentStatus() {
  return useQuery({
    queryKey: ["auth", "consent"],
    queryFn: fetchConsentStatus,
    staleTime: 5 * 60 * 1000,
  });
}

export function useIsManager() {
  const { data: user } = useCurrentUser();
  return user?.roles.includes(ROLE_MANAGER) ?? false;
}

export function useIsDriver() {
  const { data: user } = useCurrentUser();
  return user?.roles.includes(ROLE_DRIVER) ?? false;
}
