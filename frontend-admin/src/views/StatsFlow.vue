<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button @click="$router.push('/stats')" :icon="ArrowLeft">返回</el-button>
      <h2 style="margin:0">流水统计</h2>
    </div>

    <el-card style="margin-bottom:20px">
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <span style="font-weight:bold;font-size:15px">统计时间段</span>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width:280px"
          @change="loadAll"
        />
        <el-button @click="setToday">今天</el-button>
        <el-button @click="setThisWeek">本周</el-button>
        <el-button @click="setThisMonth">本月</el-button>
      </div>
    </el-card>

    <el-card style="margin-bottom:16px">
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <div style="flex:1;min-width:120px;background:linear-gradient(135deg,#f0f9eb,#d4edda);border-radius:8px;padding:12px;text-align:center">
          <div style="font-size:12px;color:#666;margin-bottom:4px">销售收入</div>
          <div style="font-size:20px;font-weight:bold;color:#67c23a">${{ flowData.total_sales }}</div>
        </div>
        <div style="flex:1;min-width:120px;background:linear-gradient(135deg,#fef0f0,#fdd);border-radius:8px;padding:12px;text-align:center">
          <div style="font-size:12px;color:#666;margin-bottom:4px">入库支出</div>
          <div style="font-size:20px;font-weight:bold;color:#f56c6c">${{ flowData.total_cost }}</div>
        </div>
        <div :style="`flex:1;min-width:120px;background:${flowData.profit >= 0 ? 'linear-gradient(135deg,#e8f4fd,#c3dff7)' : 'linear-gradient(135deg,#fef0f0,#fdd)'};border-radius:8px;padding:12px;text-align:center`">
          <div style="font-size:12px;color:#666;margin-bottom:4px">{{ flowData.profit >= 0 ? '盈利' : '亏损' }}</div>
          <div :style="`font-size:20px;font-weight:bold;color:${flowData.profit >= 0 ? '#409eff' : '#f56c6c'}`">${{ Math.abs(flowData.profit) }}</div>
        </div>
      </div>
    </el-card>

    <el-card>
      <template #header><span>流水明细</span></template>

      <!-- PC端表格 -->
      <el-table v-if="!isMobile" :data="flowData.records" stripe max-height="600">
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === '销售' ? 'success' : 'warning'" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="90">
          <template #default="{ row }">${{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span :style="row.type === '销售' ? 'color:#67c23a;font-weight:bold' : 'color:#f56c6c'">
              {{ row.type === '销售' ? '+' : '-' }}${{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
      </el-table>

      <!-- 手机端卡片 -->
      <div v-if="isMobile">
        <div
          v-for="(row, idx) in flowData.records" :key="idx"
          style="border:1px solid #e4e7ed;border-radius:8px;padding:12px;margin-bottom:10px;background:#fff"
        >
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
            <div style="font-weight:bold;font-size:14px;flex:1;margin-right:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ row.product_name }}</div>
            <el-tag :type="row.type === '销售' ? 'success' : 'warning'" size="small">{{ row.type }}</el-tag>
          </div>
          <div style="font-size:12px;color:#888;margin-bottom:6px">{{ row.time }}</div>
          <div style="display:flex;gap:16px;font-size:13px;flex-wrap:wrap">
            <span>数量：<b>{{ row.quantity }}</b></span>
            <span>单价：<b>${{ row.unit_price }}</b></span>
            <span>金额：
              <b :style="row.type === '销售' ? 'color:#67c23a' : 'color:#f56c6c'">
                {{ row.type === '销售' ? '+' : '-' }}${{ row.amount }}
              </b>
            </span>
          </div>
          <div v-if="row.remark" style="font-size:12px;color:#aaa;margin-top:4px">备注：{{ row.remark }}</div>
        </div>
        <div v-if="flowData.records.length === 0" style="text-align:center;color:#aaa;padding:40px 0">暂无记录</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'

const dateRange = ref(null)
const flowData = ref({ total_sales: 0, total_cost: 0, profit: 0, records: [] })
const isMobile = ref(window.innerWidth <= 768)
window.addEventListener('resize', () => { isMobile.value = window.innerWidth <= 768 })

const getParams = () => {
  if (dateRange.value && dateRange.value[0]) {
    return { start: dateRange.value[0], end: dateRange.value[1] }
  }
  const today = new Date().toISOString().slice(0, 10)
  return { start: today, end: today }
}

const loadAll = async () => {
  const params = getParams()
  flowData.value = await request.get('/stats/flow', { params })
}

const setToday = () => {
  const today = new Date().toISOString().slice(0, 10)
  dateRange.value = [today, today]
  loadAll()
}

const setThisWeek = () => {
  const now = new Date()
  const day = now.getDay() || 7
  const mon = new Date(now)
  mon.setDate(now.getDate() - day + 1)
  dateRange.value = [mon.toISOString().slice(0, 10), now.toISOString().slice(0, 10)]
  loadAll()
}

const setThisMonth = () => {
  const now = new Date()
  const first = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10)
  dateRange.value = [first, now.toISOString().slice(0, 10)]
  loadAll()
}

onMounted(() => {
  setToday()
})
</script>