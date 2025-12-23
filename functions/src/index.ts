/**
 * Flourisha Firebase Cloud Functions
 *
 * Handles user provisioning with custom claims for multi-tenant architecture
 */

import * as functions from "firebase-functions";
import * as admin from "firebase-admin";

// Initialize Firebase Admin
admin.initializeApp();

// Default tenant configuration
const DEFAULT_TENANT_ID = "mk3029839"; // CoCreators tenant

/**
 * Triggered when a new user is created in Firebase Auth
 * Automatically assigns custom claims for multi-tenant access
 *
 * Claims set:
 * - tenant_id: Organization/tenant identifier
 * - tenant_user_id: User's ID within the tenant (same as Firebase UID)
 * - role: User role (default: 'user')
 * - groups: Array of group memberships
 */
export const onUserCreate = functions.auth.user().onCreate(async (user) => {
  const { uid, email } = user;

  functions.logger.info(`New user created: ${email} (${uid})`);

  // Custom claims to assign
  const customClaims = {
    tenant_id: DEFAULT_TENANT_ID,
    tenant_user_id: uid,
    role: "user",
    groups: [] as string[],
  };

  try {
    // Set custom claims on the user
    await admin.auth().setCustomUserClaims(uid, customClaims);

    functions.logger.info(`Custom claims set for user ${uid}:`, customClaims);

    // Optional: Create user record in Supabase
    // This could be done via HTTP call to your backend or direct Supabase access
    // For now, we just set the claims and let the backend handle DB creation on first API call

    return { success: true, uid, claims: customClaims };
  } catch (error) {
    functions.logger.error(`Failed to set custom claims for ${uid}:`, error);
    throw new functions.https.HttpsError(
      "internal",
      `Failed to provision user: ${error}`
    );
  }
});

/**
 * HTTP endpoint to manually set custom claims for a user
 * Useful for admin operations or fixing existing users
 *
 * Requires admin authentication (service account or admin user)
 */
export const setUserClaims = functions.https.onCall(async (data, context) => {
  // Verify caller is admin
  if (!context.auth?.token?.role || context.auth.token.role !== "admin") {
    throw new functions.https.HttpsError(
      "permission-denied",
      "Only admins can set user claims"
    );
  }

  const { targetUid, tenantId, role, groups } = data;

  if (!targetUid) {
    throw new functions.https.HttpsError(
      "invalid-argument",
      "targetUid is required"
    );
  }

  const customClaims = {
    tenant_id: tenantId || DEFAULT_TENANT_ID,
    tenant_user_id: targetUid,
    role: role || "user",
    groups: groups || [],
  };

  try {
    await admin.auth().setCustomUserClaims(targetUid, customClaims);
    functions.logger.info(`Admin updated claims for ${targetUid}:`, customClaims);
    return { success: true, uid: targetUid, claims: customClaims };
  } catch (error) {
    functions.logger.error(`Failed to update claims for ${targetUid}:`, error);
    throw new functions.https.HttpsError(
      "internal",
      `Failed to update claims: ${error}`
    );
  }
});

/**
 * HTTP endpoint to provision all existing users without claims
 * One-time migration function
 */
export const provisionExistingUsers = functions.https.onCall(
  async (_data, context) => {
    // Verify caller is admin
    if (!context.auth?.token?.role || context.auth.token.role !== "admin") {
      throw new functions.https.HttpsError(
        "permission-denied",
        "Only admins can run migrations"
      );
    }

    const results: Array<{ uid: string; email?: string; status: string }> = [];
    let nextPageToken: string | undefined;

    try {
      do {
        const listResult = await admin.auth().listUsers(1000, nextPageToken);

        for (const user of listResult.users) {
          const existingClaims = user.customClaims || {};

          // Skip if already has tenant_id
          if (existingClaims.tenant_id) {
            results.push({
              uid: user.uid,
              email: user.email,
              status: "skipped - already has claims",
            });
            continue;
          }

          // Set claims
          const customClaims = {
            tenant_id: DEFAULT_TENANT_ID,
            tenant_user_id: user.uid,
            role: "user",
            groups: [],
          };

          await admin.auth().setCustomUserClaims(user.uid, customClaims);
          results.push({
            uid: user.uid,
            email: user.email,
            status: "provisioned",
          });
        }

        nextPageToken = listResult.pageToken;
      } while (nextPageToken);

      functions.logger.info(`Migration complete. Processed ${results.length} users`);
      return { success: true, results };
    } catch (error) {
      functions.logger.error("Migration failed:", error);
      throw new functions.https.HttpsError(
        "internal",
        `Migration failed: ${error}`
      );
    }
  }
);
