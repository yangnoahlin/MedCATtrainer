<template>
  <div class="container-fluid demo">
    <div class="demo-text">
      <form @submit.prevent>
        <div class="form-group" >
          <label>1. 選擇模型對應的詞典:</label>
          <select class="form-control" v-model="selectedProject">
            <option :value="proj" v-for="proj of projects" :key="proj.id">{{proj.name}}
            </option>
          </select>
        </div>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
          <button @click="reload()" class="btn btn-primary" style="flex: 1;">2.載入最新的處理進度</button><p></p>
        </div>          
        <div class="form-group">
          <label>3.請選擇病例:</label>
          
          <select class="form-control" v-model="selectedRecord" @change="handleRecordSelection">
            <option
              :value="record"
              v-for="record of records"
              :key="record.sqe"
              :disabled="record.status !== 'uploaded'"
            >
              {{record.sqe}}-{{record.status}}
            </option>
          </select>
        </div>
        <div class="form-group" :style="{ visibility: 'hidden' }" >
          <label>病例內容:</label>
          <textarea v-model="exampleText" class="form-control" name="text" rows="10"></textarea>
        </div>
        <div class="form-group" :style="{ visibility: 'hidden' }" >
          <label>CUI 過濾清單</label>
          <textarea v-model="cuiFilters" class="form-control" name="cui"
                    rows="3" placeholder="Comma separated list: S-91175000, S-84757009"></textarea>
        </div>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
          <button @click="fetchNerResult()" class="btn btn-primary" style="flex: 1;">4.顯示分析結果</button>
          <!-- <button @click="fetchLlmResult()" class="btn btn-primary" style="flex: 1;">4-2.LLM 結果</button> -->
        </div>
        <p></p>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
          <button @click="setConfirmedStatus(true)" class="btn btn-success" style="flex: 1;">分析正確</button>
          <button @click="setConfirmedStatus(false)" class="btn btn-danger" style="flex: 1;">分析錯誤</button>
        </div>
      </form>
    </div>
    <div class="view-port">
      <div class="clinical-text">
        <clinical-text :loading="loadingMsg" :text="annotatedText" :ents="ents"
                       :taskName="task" :taskValues="taskValues" @select:concept="selectEntity"></clinical-text>
      </div>
      <div class="sidebar">
        <concept-summary :selectedEnt="currentEnt" :project="selectedProject"
                         :searchFilterDBIndex="searchFilterDBIndex"
                         :llmResult="llmResultFromDemo"
                         :confirmedText="confirmedTextFromDemo"></concept-summary>
      </div>
    </div>
  </div>
</template>

<script>
import ClinicalText from '@/components/common/ClinicalText.vue'
import ConceptSummary from '@/components/common/ConceptSummary.vue'

const TASK_NAME = 'Concept Anno'
const VALUES = ['Val']

export default {
  name: 'Demo',
  components: {
    ClinicalText,
    ConceptSummary
  },
  data () {
    return {
      exampleText: '',
      projects: [],
      selectedProject: {},
      records: [],
      selectedRecord: {},
      cuiFilters: '',
      ents: [],
      currentEnt: {},
      annotatedText: '',
      loadingMsg: null,
      task: TASK_NAME,
      taskValues: VALUES,
      searchFilterDBIndex: null,
      llmResultFromDemo: "",
      confirmedTextFromDemo: ""
    }
  },
  created () {
    let projectList = []
    let that = this
    const baseUrl = '/api/project-annotate-entities/'
    let getProjects = function (url) {
      that.$http.get(url).then(resp => {
        if (resp.data.count === (projectList.length + resp.data.results.length)) {
          that.projects = projectList.concat(resp.data.results)
        } else {
          const nextUrl = `${baseUrl}?${resp.data.next.split('?').slice(-1)}`
          projectList = projectList.concat(resp.data.results)
          getProjects(nextUrl)
        }
      })
    }
    getProjects(baseUrl)
  },
  methods: {
    reload () {
      this.loadingResult = true;
      const payload = {
        
      };
      this.$http.post('http://localhost:62593/txt_ner_list', payload).then(resp => {
        this.records = resp.data.records;
      }).catch(error => {
        console.error("Error loading records:", error);
      });
    },
    handleRecordSelection() {
      // 当选择发生变化时执行的逻辑
      this.exampleText = this.selectedRecord.text;
      this.annotatedText = this.selectedRecord.text;
      // 你可以在这里触发其他的逻辑或函数
    },
    fetchNerResult () {
      // const payloadNerResult = {
      //   sqe: this.selectedRecord.sqe,
      //   text: this.exampleText,
      //   cuis: this.cuiFilters,
      // }
      // this.loadingMsg = 'Fetch NER Result...'
      // this.$http.post('http://localhost:62593/txt_ner_result', payloadNerResult).then(resp => {
      //   this.loadingMsg = null
      //   this.ents = resp.data['entities'].map(e => {
      //     e.assignedValues = {}
      //     e.assignedValues[this.task] = this.taskValues[0]
      //     return e
      //   })
      //   this.currentEnt = this.ents.length > 0 ? this.ents[0] : null
      //   this.annotatedText = resp.data['text']
      // })
      const payloadLlmResult = {
        sqe: this.selectedRecord.sqe,
      }
      this.loadingMsg = 'Fetch LLM Result...'
      this.$http.post('http://localhost:62593/txt_llm_result', payloadLlmResult).then(resp => {
        this.loadingMsg = null
        this.llmResultFromDemo = JSON.stringify(resp.data, null, 2)
      })
      const payloadGetStatus = {
        sqe: this.selectedRecord.sqe,
      }
      this.$http.post('http://localhost:62593/get_confirmed_status', payloadGetStatus).then(resp => {
        console.log(resp.data)
        if (!('is_confirmed' in resp.data) || resp.data['is_confirmed'] === null) {
          console.log("為確認")
          this.confirmedTextFromDemo = "待確認"
        } else if (resp.data['is_confirmed'] === true) {
          console.log("正確")
          this.confirmedTextFromDemo = "正確"
        } else if (resp.data['is_confirmed'] === false) {
          console.log("錯誤")
          this.confirmedTextFromDemo = "錯誤"
        }
        
      })
    },
    fetchLlmResult () {
      const payloadLlmResult = {
        sqe: this.selectedRecord.sqe,
      }
      this.loadingMsg = 'Fetch LLM Result...'
      this.$http.post('http://localhost:62593/txt_llm_result', payloadLlmResult).then(resp => {
        this.loadingMsg = null
        this.llmResultFromDemo = resp.data['entities']
        this.confirmedTextFromDemo = "n/a"
      })
    },
    setConfirmedStatus (isConfirmed) {
      const payloadSetStatus = {
        sqe: this.selectedRecord.sqe,
        is_confirmed: isConfirmed
      }
      this.$http.post('http://localhost:62593/set_confirmed_status', payloadSetStatus).then(resp => {
        this.confirmedTextFromDemo = isConfirmed ? "正確":"錯誤"
      })
    },
    annotate () {
      const payload = {
        project_id: this.selectedProject.id,
        message: this.exampleText,
        cuis: this.cuiFilters,
      }
      this.loadingMsg = 'Annotating Text...'
      this.$http.post('/api/annotate-text/', payload).then(resp => {
        this.loadingMsg = null
        this.ents = resp.data['entities'].map(e => {
          e.assignedValues = {}
          e.assignedValues[this.task] = this.taskValues[0]
          return e
        })
        this.currentEnt = this.ents.length > 0 ? this.ents[0] : null
        this.annotatedText = resp.data['message']
      })
    },
    selectEntity (entIndex) {
      this.currentEnt = this.ents[entIndex]
    },
    fetchCDBSearchIndex () {
      if (this.selectedProject.cdb_search_filter.length > 0) {
        this.$http.get(`/api/concept-dbs/${this.selectedProject.cdb_search_filter[0]}/`).then(resp => {
          if (resp.data) {
            this.searchFilterDBIndex = `${resp.data.name}_id_${this.selectedProject.cdb_search_filter}`
          }
        })
      }
    }
  },
  watch: {
    'selectedProject': {
      handler () {
        this.fetchCDBSearchIndex()
      }
    }
  }
}
</script>

<style scoped lang="scss">
.demo {
  height: calc(100% - 71px);
  display: flex;
}

.demo-text {
  flex-direction: column;
  flex: 0 0 400px;
  height: 100%;
}

.view-port {
  flex: 1 1 auto;
  display: flex;
}

.clinical-text {
  height:100%;
  flex-direction: column;
  flex: 1 1 auto;
}

.sidebar {
  height:100%;
  flex-direction: column;
  flex: 0 0 350px;
}

form {
  margin: 5%;
}
</style>
