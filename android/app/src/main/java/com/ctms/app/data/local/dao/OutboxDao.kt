package com.ctms.app.data.local.dao

import androidx.room.*
import com.ctms.app.data.local.entity.OutboxMutationEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface OutboxDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMutation(mutation: OutboxMutationEntity)

    @Query("SELECT * FROM outbox_mutations WHERE status IN ('QUEUED', 'FAILED') ORDER BY createdAt ASC")
    suspend fun getPendingMutations(): List<OutboxMutationEntity>

    @Query("SELECT COUNT(*) FROM outbox_mutations WHERE status IN ('QUEUED', 'FAILED')")
    fun getPendingCountFlow(): Flow<Int>

    @Query("UPDATE outbox_mutations SET status = :newStatus WHERE mutationId = :id")
    suspend fun updateStatus(id: String, newStatus: String)

    @Query("UPDATE outbox_mutations SET status = 'FAILED', lastError = :error, retryCount = retryCount + 1 WHERE mutationId = :id")
    suspend fun recordFailure(id: String, error: String)

    @Query("DELETE FROM outbox_mutations WHERE status = 'COMMITTED' AND createdAt < :thresholdTimestamp")
    suspend fun purgeOldCommitted(thresholdTimestamp: Long)
}
