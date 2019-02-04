
class WpcGenerator():

    def __init__(self, cfg, helper, ssaString):
        self.cfg = cfg
        self.helper = helper
        self.ssaString = ssaString

        self.finalWpcString = ""
        self.totalNodeCount = -1
        self.cfgVisited = []


    def execute(self):
        self.totalNodeCount = len(self.cfg.nodes.keys())
        self.cfgVisited = [0] * self.totalNodeCount     # initialize visited list
        currentNodeId = self.totalNodeCount - 1
        # self.runner(currentNodeId)        # 1st approach
        # self.goodAlgo(currentNodeId, "")    # 2nd approach
        self.wpcStringMakerAlgo(currentNodeId, "")      # modified 2nd approach


    ### modifying 2nd approach...

    def wpcStringMakerAlgo(self, currentNodeId, wpcString):
        if self.cfgVisited[currentNodeId] == 1:
            return
        currentNode = self.cfg.nodes[currentNodeId]
        if len(currentNode.next) > 1:       # it's a condition! Yo!!!
            listOfNext = list(currentNode.next)
            if self.cfgVisited[listOfNext[0]]==1 and self.cfgVisited[listOfNext[1]]==1:
                # Beware! first enrich wpcMakerHelper dict()
                self.enrich_wpcMakerHelper(currentNodeId, wpcString)
                # merge true and false part
                print("----", str(currentNodeId), "---", currentNode.wpcMakerHelper)
                conditionalString = "( " + self.ssaString.getTerminal(currentNode.ctx) + " )"
                wpcString = self.mergeConditionalWpcStrings(currentNode, conditionalString)
            elif self.cfgVisited[listOfNext[0]]==1:
                self.addWpcString(currentNodeId, listOfNext[0], wpcString)
                return
            elif self.cfgVisited[listOfNext[1]]==1:
                self.addWpcString(currentNodeId, listOfNext[1], wpcString)
                return
        self.cfgVisited[currentNodeId] = 1  # visit the node
        # print(str(currentNodeId), "visited, wpc :", wpcString)
        if len(currentNode.next) <= 1:      # avoid conditional node for wpcString here
            if not currentNode.ctx == None:     # check if ctx is None
                if self.helper.getRuleName(currentNode.ctx) == "assert_statement":
                    wpcString = "( " + self.ssaString.getTerminal(currentNode.ctx.children[1]) + " )"         # start wpcString here.
                elif self.helper.getRuleName(currentNode.ctx) == "assume_statement":
                    assumeCondition = "( " + self.ssaString.getTerminal(currentNode.ctx.children[1]) + " )"
                    wpcString = "( " + assumeCondition + " ==> " + wpcString + " )"
                    # one may want to finalize and return here...   # TODO: decide later, what to do here for ASSUME
                    # self.finalWpcString = wpcString
                    # return
                elif not wpcString == "":
                    wpcString = self.updateWpcStringByReplacing(wpcString, currentNode)
                    # print(wpcString)
        # go to parents...
        if len(currentNode.parent) < 1:
            self.finalWpcString = wpcString
            return
        elif len(currentNode.parent) == 1:
            parent = set(currentNode.parent)
            self.wpcStringMakerAlgo(parent.pop(), wpcString)
        elif len(currentNode.parent) > 1:
            setOfParents = set(currentNode.parent)
            while len(setOfParents) >= 1:
                tempNodeId = setOfParents.pop()
                self.wpcStringMakerAlgo(tempNodeId, wpcString)


    def mergeConditionalWpcStrings(self, currentNode, conditionalString):
        tempString1 = ""
        tempString2 = ""
        if not currentNode.wpcMakerHelper['true'] == "":
            tempString1 = "( " + conditionalString + " ^ " + currentNode.wpcMakerHelper['true'] + " )"
        if not currentNode.wpcMakerHelper['false'] == "":
            tempString2 = "( !" + conditionalString + " ^ " + currentNode.wpcMakerHelper['false'] + " )"
        wpcString = ""
        if tempString1 == "":
            wpcString = tempString2
        elif tempString2 == "":
            wpcString = tempString1
        else:
            wpcString = "( " + tempString1 + " v " + tempString2 + " )"
        return wpcString


    # def updateWpcStringByReplacing(self, wpcString, currentNode):   # this is better than "updateWpcStringBySplitting" method
    #     wpcString = wpcString.replace("  ", " ").strip()
    #     if len(currentNode.variableLHS) > 0:
    #         for i in currentNode.variableLHS:
    #             if self.helper.getRuleName(currentNode.ctx) == "assignment_statement":  # strictly assignment_statement
    #                 replacedBy = "( " + self.ssaString.getTerminal(currentNode.ctx.children[2]) + " )"
    #                 wpcString = wpcString.replace(" "+i.strip()+" ", " "+replacedBy+" ")
    #     return wpcString

    def updateWpcStringByReplacing(self, wpcString, currentNode):   # this is better than "updateWpcStringBySplitting" method
        wpcString = wpcString.replace("  ", " ").strip()
        if len(currentNode.variableLHS) > 0:
            if self.helper.getRuleName(currentNode.ctx) == "assignment_statement":  # strictly assignment_statement
                for i in currentNode.variableLHS:
                    replacedBy = "( " + self.ssaString.getTerminal(currentNode.ctx.children[2]) + " )"
                    wpcString = wpcString.replace(" "+i.strip()+" ", " "+replacedBy+" ")
            elif self.helper.getRuleName(currentNode.ctx) == "update_statement":    # Database UPDATE statement
                whereClausePosition = -1
                whereCondition = ""
                for i in range(currentNode.ctx.getChildCount()):        # finding "where_clause"...
                    if currentNode.ctx.children[i].getChildCount() > 1 and self.helper.getRuleName(currentNode.ctx.children[i]) == "where_clause":
                        whereClausePosition = i
                        whereCondition = self.getWhereCondition(currentNode.ctx.children[i].children[1])
                        print("@@@@@@@ whereCondition :", whereCondition)
                        break
                if not whereClausePosition == -1:   # whereCondition exists
                    tempWpcString = wpcString
                    updateSetCtx = currentNode.ctx.children[whereClausePosition-1]
                    for i in range(updateSetCtx.getChildCount()):       # finding "column_based_update_set_clause"...
                        if updateSetCtx.children[i].getChildCount() > 1 and self.helper.getRuleName(
                                updateSetCtx.children[i]) == "column_based_update_set_clause":
                            toBeReplaced = " " + updateSetCtx.children[i].children[0].getText().strip() + " "
                            replacedBy = " ( " + self.ssaString.getTerminal(updateSetCtx.children[i].children[2]).strip() + " ) "
                            tempWpcString = tempWpcString.replace(toBeReplaced, replacedBy)
                    # now join 'true' and 'false' like 'if' block...
                    wpcString = "( ( " + whereCondition + " ^ " + tempWpcString + " ) v ( !" + whereCondition + " ^ " + wpcString + " ) )"
                else:       # whereCondition does not exist...so, no merging like 'if' block...
                    for i in range(currentNode.ctx.getChildCount()):        # finding "update_set_clause"...
                        if currentNode.ctx.children[i].getChildCount() > 1 and self.helper.getRuleName(currentNode.ctx.children[i]) == "update_set_clause":
                            updateSetCtx = currentNode.ctx.children[i]
                            for j in range(updateSetCtx.getChildCount()):       # finding "column_based_update_set_clause"...
                                if updateSetCtx.children[j].getChildCount() > 1 and self.helper.getRuleName(
                                        updateSetCtx.children[j]) == "column_based_update_set_clause":
                                    toBeReplaced = " " + updateSetCtx.children[j].children[0].getText().strip() + " "
                                    replacedBy = " ( " + self.ssaString.getTerminal(updateSetCtx.children[j].children[2]).strip() + " ) "
                                    wpcString = wpcString.replace(toBeReplaced, replacedBy)
                            break
        return wpcString


    def getWhereCondition(self, ctx):   # considering only AND, OR, NOT as 'word' separator
        if ctx.getChildCount() == 1:
            return self.getWhereCondition(ctx.children[0])
        elif ctx.getChildCount() == 2:      # strictly for "NOT"
            if ctx.children[0].getText().strip() == "NOT":
                return "( !" + self.getWhereCondition(ctx.children[1]) + " )"
        elif ctx.getChildCount() == 3:
            operators = ['=', '>', '<', '>=', '<=', '!=', '<>', '^=', '~=']
            if ctx.children[1].getText().strip() == "AND":  # conditions separated by "AND"
                return "( " + self.getWhereCondition(ctx.children[0]) + " ^ " + self.getWhereCondition(ctx.children[2]) + " )"
            elif ctx.children[1].getText().strip() == "OR":  # conditions separated by "OR"
                return "( " + self.getWhereCondition(ctx.children[0]) + " v " + self.getWhereCondition(ctx.children[2]) + " )"
            elif ctx.children[1].getText().strip() in operators:
                return "( " + self.ssaString.getTerminal(ctx) + " )"
            else:
                return self.getWhereCondition(ctx.children[1])


    def addWpcString(self, currentNodeId, myVisitedChildId, wpcString):
        if self.cfg.nodes[currentNodeId].branching['true'] == myVisitedChildId:
            self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString    # fool! don't just edit the copy!
        elif self.cfg.nodes[currentNodeId].branching['false'] == myVisitedChildId:
            self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString

    def enrich_wpcMakerHelper(self, currentNodeId, wpcString):
        if len(self.cfg.nodes[currentNodeId].wpcMakerHelper) < 2:
            if self.cfg.nodes[currentNodeId].wpcMakerHelper.get('true') == None:
                self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString
            elif self.cfg.nodes[currentNodeId].wpcMakerHelper.get('false') == None:
                self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString




    ### 2nd approach... better complexity than 1st one

    # def goodAlgo(self, currentNodeId, wpcString):
    #     if self.cfgVisited[currentNodeId] == 1:
    #         return
    #
    #     currentNode = self.cfg.nodes[currentNodeId]
    #     if len(currentNode.next) > 1:       # it's a condition! Yo!!!
    #         listOfNext = list(currentNode.next)
    #         if self.cfgVisited[listOfNext[0]]==1 and self.cfgVisited[listOfNext[1]]==1:
    #             # Beware! first enrich wpcMakerHelper dict()
    #             self.enrich_wpcMakerHelper(currentNodeId, wpcString)
    #             # if len(currentNode.wpcMakerHelper) < 2:
    #             #     if currentNode.wpcMakerHelper.get('true') == None:
    #             #         self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString
    #             #     elif currentNode.wpcMakerHelper.get('false') == None:
    #             #         self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString
    #
    #             # merge true and false part
    #             print(listOfNext)
    #             print("-------", currentNode.wpcMakerHelper)
    #             wpcString = "( ( " + str(currentNodeId) + " ^ " + currentNode.wpcMakerHelper['true'] + " ) v ( !" + str(currentNodeId) + " ^ " + currentNode.wpcMakerHelper['false'] + " ) )"
    #         elif self.cfgVisited[listOfNext[0]]==1:
    #             print("first")
    #             self.addWpcString(currentNodeId, listOfNext[0], wpcString)
    #             # if currentNode.branching['true']==listOfNext[0]:
    #             #     self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString    # fool! don't just edit the copy!
    #             # elif currentNode.branching['false']==listOfNext[0]:
    #             #     self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString
    #             return
    #         elif self.cfgVisited[listOfNext[1]]==1:
    #             print("second")
    #             self.addWpcString(currentNodeId, listOfNext[1], wpcString)
    #             # if currentNode.branching['true']==listOfNext[1]:
    #             #     self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString
    #             # elif currentNode.branching['false']==listOfNext[1]:
    #             #     self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString
    #             return
    #
    #     self.cfgVisited[currentNodeId] = 1
    #     print(">>>", currentNodeId, "= 1")
    #     if len(currentNode.next) <= 1:      # avoid conditional node for wpcString
    #         wpcString = wpcString + "." + str(currentNodeId)
    #
    #     #..........
    #     if len(currentNode.parent) < 1:
    #         self.finalWpcString = wpcString
    #         return
    #     elif len(currentNode.parent) == 1:
    #         parent = set(currentNode.parent)
    #         self.goodAlgo(parent.pop(), wpcString)
    #     elif len(currentNode.parent) > 1:
    #         setOfParents = set(currentNode.parent)
    #         while len(setOfParents) >= 1:
    #             tempNodeId = setOfParents.pop()
    #             self.goodAlgo(tempNodeId, wpcString)
    #
    # def addWpcString(self, currentNodeId, myVisitedChildId, wpcString):
    #     if self.cfg.nodes[currentNodeId].branching['true'] == myVisitedChildId:
    #         self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString    # fool! don't just edit the copy!
    #     elif self.cfg.nodes[currentNodeId].branching['false'] == myVisitedChildId:
    #         self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString
    #
    # def enrich_wpcMakerHelper(self, currentNodeId, wpcString):
    #     if len(self.cfg.nodes[currentNodeId].wpcMakerHelper) < 2:
    #         if self.cfg.nodes[currentNodeId].wpcMakerHelper.get('true') == None:
    #             self.cfg.nodes[currentNodeId].wpcMakerHelper['true'] = wpcString
    #         elif self.cfg.nodes[currentNodeId].wpcMakerHelper.get('false') == None:
    #             self.cfg.nodes[currentNodeId].wpcMakerHelper['false'] = wpcString


    ### 1st approach...

    # def runner(self, currentNodeId):
    #     print(currentNodeId, end=" ")
    #     if len(self.cfg.nodes[currentNodeId].parent) < 1:
    #         return
    #     else:
    #         setOfParents = set(self.cfg.nodes[currentNodeId].parent)
    #         while len(setOfParents) >= 1:
    #             tempNodeId = setOfParents.pop()
    #             self.runner(tempNodeId)