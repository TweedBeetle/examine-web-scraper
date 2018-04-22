import dill

with open('resp', 'rb') as f:
    response = dill.load(f)

numerical_grade = lambda grade: 5 - (ord(str(grade)) - 96)

def numeric_magnitude(magnitude):
    if magnitude == 'Minor':
        return 1
    elif magnitude == 'Notable':
        return 2
    elif magnitude == 'Strong':
        return 3
    else:
        raise ValueError('{} is not a valid magnitude'.format(magnitude))

def numeric_magnitude_direction(direction):
    if direction == 'up':
        return 1
    elif direction == 'down':
        return -1
    else:
        raise ValueError('{} is not a valid direction'.format(direction))

def numerical_consistency(consistency):
    if consistency == 'Very High':
        return 4
    elif consistency == 'High':
        return 3
    elif consistency == 'Moderate':
        return 2
    elif consistency == 'Low':
        return 1
    else:
        raise ValueError('{} is not a valid consistency'.format(consistency))

summary_xpath = '/html/body/main/section[@class="grid--main"]/div/div/div/article[@id="summary"]/p/text()'
summary_parts = response.xpath(summary_xpath).extract()
summary_parts = [str(summary_part) for summary_part in summary_parts]
summary = '\n'.join(summary_parts)
supplement_name = response.url.split('/')[-2]
supplement_info = dict(
    name=supplement_name,
    outcomes=dict(),
    summary=summary
)
outcome_rows_xpath = '/html/body/main/section[@class="grid--main"]/div/div/div[1]/article[@id="effect-matrix"]/div[@class="result"]/table/tbody/tr[*]'
outcomes = response.xpath(outcome_rows_xpath)
for outcome in outcomes:
    outcome_name = str(outcome.extract().split('"')[1].replace('hem-', ''))
    outcome_grade_image_source = outcome.xpath('td[1]/img/@pagespeed_lazy_src').extract()[0]
    outcome_grade_string = outcome_grade_image_source[-5]
    outcome_grade = numerical_grade(outcome_grade_string)
    outcome_magnitude_string = outcome.xpath('td[3]/span[@class="sl-text"]/text()').extract()
    if len(outcome_magnitude_string) == 0:
        outcome_magnitude = None
    else:
        outcome_magnitude = numeric_magnitude(outcome_magnitude_string[0])
        outcome_magnitude_direction = outcome.xpath('td[3]/img/@pagespeed_lazy_src').extract()[0].split('-')[-2]
        if outcome_magnitude_direction in ['up', 'down']:
            outcome_magnitude *= numeric_magnitude_direction(outcome_magnitude_direction)
        elif outcome_magnitude_direction == 'examinecdn.scdn5.secure.raxcdn.com/assets/v7/images/icons/icon':
            outcome_magnitude = None
        else:
            raise ValueError('{} is not a valid magnitude'.format(outcome_magnitude_direction))
    outcome_consistency_string = outcome.xpath('td[4]/strong/text()').extract()[0].strip()
    outcome_consistency = numerical_consistency(outcome_consistency_string)
    try:
        outcome_notes = str(outcome.xpath('td[5]/div/text()').extract()[0].strip())
    except UnicodeEncodeError as e:
        outcome_notes = outcome.xpath('td[5]/div/text()').extract()[0].strip()

    if outcome_notes == '':
        outcome_notes = None
    supplement_info['outcomes'][outcome_name] = dict(
        grade=outcome_grade,
        magnitude=outcome_magnitude,
        consistency=outcome_consistency,
        notes=outcome_notes
    )
