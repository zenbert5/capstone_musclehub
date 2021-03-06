"""
CAPSTONE Project - MuscleHub Inc.
Objective: Analyze MuscleInc's marketing and sales campaign to bring in more members through
    sign-up process of conducting a fitness test or without.  Evaluate if the results and their significance
    for recommendations

CodeAcademy - 12/2017 - 01/2018
Shawn Chen (Analyst)

version 1.0

"""


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency

# Create multiple join query of tables into one and assign to dataframe df
df = sql_query('''
SELECT v.first_name, v.last_name, v.gender, v.email, v.visit_date, ft.fitness_test_date, ap.application_date, ps.purchase_date
FROM visits AS v
LEFT JOIN fitness_tests AS ft
ON (v.first_name = ft.first_name 
    AND v.last_name = ft.last_name 
    AND v.email = ft.email
    )
LEFT JOIN applications AS ap
ON (v.first_name = ap.first_name
    AND v.last_name = ap.last_name
    AND v.email = ap.email
    )
LEFT JOIN purchases AS ps
ON (v.first_name = ps.first_name
    AND v.last_name = ps.last_name
    AND v.email = ps.email
    )
WHERE v.visit_date >= '7-1-17'
''')

# print dataframe and stats
print df.head(), df.count()

# create data field to designate A/B groups
df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'A' if pd.notnull(x) else 'B')

# create subframe of A/B groups by email (of each test group)
ab_counts = df.groupby('ab_test_group').email.count().reset_index()

# create pie chart illustrating the percentage difference between the groups
pie_halves = ['Had Fitness Test', 'No Fitness Test']
plt.pie(ab_counts.email, autopct='%.2f')
plt.axis('equal')
plt.legend(pie_halves)
plt.title('Visitors Distribution - Fitness Test v. No Fitness Test')

plt.savefig('fall_visitors.png')
plt.show()

# create data field to label if visitor applied for membership and organize dataframe to show A/B groups + application status
df['is_application'] = df.application_date.apply(lambda x: 'Application' if pd.notnull(x) else 'No Application')
app_counts = df.groupby(['ab_test_group', 'is_application']).email.count().reset_index()

# create pivot table for visual aid
app_pivot = app_counts.pivot(
    columns = 'is_application',
    index = 'ab_test_group',
    values = 'email'
    ).reset_index()

# create total and percentage data fields to tabulate totol and percentage applied
app_pivot['Total'] = app_pivot['Application'] + app_pivot['No Application']
app_pivot['Percent'] = app_pivot['Application'] / app_pivot['Total']

print app_pivot

# calculate pval for significance against null hypothesis
contingency = [[app_pivot['Application'][0], app_pivot['No Application'][0]],
               [app_pivot['Application'][1], app_pivot['No Application'][1]]]

chi2, app_pval, dof, expected = chi2_contingency(contingency)
print app_pval


# create data field to identify visitors that became (paid) members
df['is_member'] = df.purchase_date.apply(lambda x: 'Member' if pd.notnull(x) else 'Not Member')

just_apps = df[df.is_application == 'Application']

# create pivot table to show the distribution of A/B groups that applied and became members
member_count = just_apps.groupby(['ab_test_group', 'is_member']).email.count().reset_index()
member_pivot = member_count.pivot(
    columns = 'is_member',
    index = 'ab_test_group',
    values = 'email'
    ).reset_index()

member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot['Member'] / member_pivot['Total']
print member_pivot

# calculate the significance of A/B applicants becoming members
contingency = [[member_pivot['Member'][0], member_pivot['Not Member'][0]],
               [member_pivot['Member'][1], member_pivot['Not Member'][1]]]

chi2, m_pval, dof, expected = chi2_contingency(contingency)
print m_pval


# calculate all visitors that became members from the A/B groups
all_visitors_purchased = df.groupby(['ab_test_group', 'is_member']).email.count().reset_index()

final_member_pivot = all_visitors_purchased.pivot(
    columns = 'is_member',
    index = 'ab_test_group',
    values = 'email'
    ).reset_index()

final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot['Member'] / final_member_pivot['Total']

print final_member_pivot

# calculate significance
contingency = [[final_member_pivot['Member'][0], final_member_pivot['Not Member'][0]],
               [final_member_pivot['Member'][1], final_member_pivot['Not Member'][1]]]

chi2, fm_pval, dof, expected = chi2_contingency(contingency)

print fm_pval

# prepare presentation visual aid
# plot side-by-side graphs to illustrate findings
# 1 - A/B groups that applied
# 2 - A/B groups applicants that purchased membership
# 3 - percentage of visitors who purchased a membership

# 1:3
plot_data = app_pivot['Percent'].values
bar_input = range(len(app_pivot)

ax = plt.subplot()
bar = plt.bar(bar_input, plot_data, color='b')
bar[0].set_color('r')

ax.set_xticks([0, 1])
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
for i, v in enumerate(plot_data):
    ax.text(i, v+1, str(round(v, 2)), horizontalalignment='center', fontsize=12, fontweight='bold')
plt.xlabel('Application Groups')
plt.ylabel('Percentage Applied')
plt.title('Applications by Group', fontweight='bold')

plt.savefig('applicants_by_group.png')
plt.show()

# 2:3
plot_data = member_pivot['Percent'].values
bar_input = range(len(member_pivot)

ax = plt.subplot()
bar = plt.bar(bar_input, plot_data, color='b')
bar[0].set_color('r')

ax.set_xticks([0, 1])
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.25, 0.50, 0.75, 1.00])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
for i, v in enumerate(plot_data):
    ax.text(i, v+1, str(round(v, 2)), horizontalalignment='center', fontsize=12, fontweight='bold')
plt.xlabel('Application Groups')
plt.ylabel('Percentage Purchased Membership')
plt.title('Purchased Membership by Applicant Group', fontweight='bold')

plt.savefig('purchased_by_application_group.png')
plt.show()


# 3:3
plot_data = final_member_pivot['Percent'].values
bar_input = range(len(final_member_pivot)

ax = plt.subplot()
bar = plt.bar(bar_input, plot_data, color='b')
bar[0].set_color('r')

ax.set_xticks([0, 1])
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.175])
ax.set_yticklabels(['0%', '2.5%', '5%', '7.5%', '10%', '12.5%', '15%', '17.5%'])
for i, v in enumerate(plot_data):
    ax.text(i, v+1, str(round(v, 2)), horizontalalignment='center', fontsize=12, fontweight='bold')
plt.xlabel('Application Groups')
plt.ylabel('Percentage Purchased Membership')
plt.title('All Visitors Purchased Membership by Group', fontweight='bold')

plt.savefig('all_visitors_purchased_by_group.png')
plt.show()
