### START MONKEY PATCH ###

# NOTE1: CHANGE THIS TO SUBCLASS. MONKEY PATCHING IS STUPID WHAT WAS I THINKING???

# NOTE2: THE POINT OF THIS CODE WAS TO EFFICIENTLY CHECK FILTERS AGAINST SQL OBJECTS
# ALREADY LOADED IN THE DATABSE, BUT CERTAIN QUERIES THAT USE THE LOCATIONS TABLE
# OR PAGES (LIKES) CANNOT BE DONE IN THIS MANNER.

# Because of NOTE2, I'm abandoning this approach and trying to create subqueries 
# for each user instead. The end result is that I MUST do this through postgres
# somehow so that postgres can handle things like ilike_op or between_op and I don't
# need to write custom code for everything.

from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, ClauseList
from sqlalchemy.sql.operators import ilike_op, between_op
from sqlalchemy.orm.evaluator import EvaluatorCompiler, UnevaluatableError
from sqlalchemy.sql import sqltypes
orignal_process = EvaluatorCompiler.process
original_visit_binary = EvaluatorCompiler.visit_binary
original_visit_clauselist = EvaluatorCompiler.visit_clauselist

def patched_process(self, clause):
    try:
        truth_value = orignal_process(self, clause)
        if truth_value == None:
            raise

        return truth_value
    except UnevaluatableError:

        if  clause.__visit_name__ == "select":
            print "i need to handle this special case for select clause"
            print "this is happening when i'm using a relatinship on the"
            print "user model like pages or locations"
            import pdb; pdb.set_trace()

        else:
            raise

def patched_visit_binary(self, clause):
    try:
        truth_value = original_visit_binary(self, clause)
        if truth_value == None:
            raise
        return truth_value
    except UnevaluatableError:
        
        column, bind_parameter = clause.get_children()

        if clause.operator == ilike_op:
            if type(column.type) == sqltypes.String and type(bind_parameter.type) == sqltypes.String:
                return lambda obj: re.search(bind_parameter.value, getattr(obj, column.name), re.IGNORECASE) if getattr(obj, column.name) else False
            else:
                raise
        elif clause.operator == between_op:

            if type(bind_parameter) == ClauseList:
                if len(bind_parameter.clauses) == 2:

                    clause1 = bind_parameter.clauses[0]
                    clause2 = bind_parameter.clauses[1]
                    
                    if type(clause1.type) == sqltypes.DateTime and type(clause2.type) == sqltypes.DateTime:
                        
                        date1 = clause1.value
                        date2 = clause2.value

                        def compare_date(obj):
                            obj_date = getattr(obj, column.name)
                            # print "date1", date1
                            # print "date2", date2
                            # print "obj_date", obj_date
                            # print date1.date() <= obj_date
                            # print obj_date < date2.date()
                            # print date1.date() <= obj_date and obj_date < date2.date()

                            # truth_value = (obj_date < date2.date()) and (date1.date() <= obj_date)

                            # print date1.date()
                            # print date2.date()
                            # print obj_date

                            if obj_date == None: return False

                            return (obj_date < date2.date()) and (date1.date() <= obj_date)
                        return compare_date
                    else:
                        raise
                else:
                    raise 
            else:
                raise
        else:
            raise

EvaluatorCompiler.process = patched_process
EvaluatorCompiler.visit_binary = patched_visit_binary

#### END MONKEY PATCH ###
