import { UserCreateForm } from "@/features/users/components/user-create-form"
import { UsersTable } from "@/features/users/components/users-table"
import { useUsers } from "@/features/users/hooks/use-users"
import type { ApiUser } from "@/lib/api/types"

type UsersManagerProps = {
  initialUsers: ApiUser[]
  currentUserId: string
}

export function UsersManager({
  initialUsers,
  currentUserId,
}: UsersManagerProps) {
  const users = useUsers(initialUsers)

  return (
    <div className="flex flex-col gap-5">
      {(users.error || users.notice) && (
        <p
          role={users.error ? "alert" : "status"}
          className={
            users.error
              ? "border border-destructive/40 bg-destructive/10 px-4 py-3 text-[13px] font-semibold text-destructive"
              : "border border-success/40 bg-success/10 px-4 py-3 text-[13px] font-semibold text-success"
          }
        >
          {users.error ?? users.notice}
        </p>
      )}
      <UserCreateForm disabled={users.isSaving} onSubmit={users.create} />
      <UsersTable
        users={users.users}
        currentUserId={currentUserId}
        disabled={users.isSaving}
        onToggleActive={(user) => void users.toggleActive(user)}
        onResetPassword={users.resetPassword}
        onRemove={(user) => void users.remove(user)}
      />
    </div>
  )
}
